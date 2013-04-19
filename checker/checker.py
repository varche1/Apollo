# -*- encoding: utf-8 -*-

import os
import re
import json
import subprocess
from uuid import uuid4
try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser
from os.path import expanduser

import abc

import pep8

import _ast

import pyflakes.checker as pyflakes


class CheckError():
    """Класс представления ошибки"""
    def __init__(self, *args, **kwargs):
        self.line_start = None
        self.line_end = None
        self.column_start = None
        self.column_end = None
        self.message = None
        self.severity = None
        self.type = None

        severities_available = ['error', 'warning']

        # Линия начала ошибки
        self.line_start = kwargs.get('line_start', None)

        # Линия конца ошибки
        self.line_end = kwargs.get('line_end', None)

        # Колонка начала ошибки
        self.column_start = kwargs.get('column_start', None)

        # Колонка конца ошибки
        self.column_end = kwargs.get('column_end', None)

        # Суровость ошибки
        self.severity = kwargs.get('severity', severities_available[0])

        if not self.severity:
            self.severity = severities_available[0]

        if self.severity not in severities_available:
            exeption = "Wrong error severity: {severity}. Available types are: {types}".format(
                severity=self.type,
                types=severities_available)
            raise Exception(exeption)

        # Сообщение ошибки
        self.message = kwargs.get('message', None)

        # Тип ошибки
        self.type = kwargs.get('type', None)

    def get_line(self):
        return self.line

    def get_message(self):
        data = self.message

        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            """"""
            # ошибка декодирования в лог

        return HTMLParser().unescape(data)


class BaseLinter(object):
    __metaclass__ = abc.ABCMeta

    def shell_out(self, cmd):
        data = None
        info = None
        home = expanduser("~")

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=info,
            cwd=home
        )

        if proc.stdout:
            data = proc.communicate()[0]
            self.parse_report(data)

        return data

    @abc.abstractmethod
    def lint(self, temp_file_path, code_source=None):
        """Метод реализующий проверку кода нужного файла на диске"""
        pass

    @abc.abstractmethod
    def parse_report(self, report_data):
        """Метод реализующий парсинг ответа от низкоуровнего проверяльщика"""
        pass


class BaseChecker(object):
    __metaclass__ = abc.ABCMeta

    def check(self, content):
        temp_file_name = "tmp-{random}.{ext}".format(ext=self.file_extension, random=str(uuid4()))
        temp_file_path = os.path.abspath(os.path.join(os.getcwd(), temp_file_name))

        try:
            with open(temp_file_path, "w") as f:
                f.write(content)

            for linter in self.linters:
                self.errors_list += linter.lint(temp_file_path, content)
        finally:
            os.remove(temp_file_path)


class CheckPhp(BaseChecker):
    def __init__(self):
        self.file_extension = 'php'

        self.errors_list = []

        self.linters = [
            PhpCodeSniffer(),
            PhpMessDetector()
        ]


class PhpCodeSniffer(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['phpcs', '--report=checkstyle', temp_file_path])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source="(?P<type>.*)"'
        lines = re.finditer(expression, report_data)

        for line in lines:
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': line.group('column'),
                'column_end':   line.group('column'),
                'message':      line.group('message'),
                'severity':     line.group('severity'),
                'type':         line.group('type')
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class PhpMessDetector(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['phpmd', temp_file_path, 'text', 'codesize,unusedcode,naming'])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'.*:(?P<line>\d+)[ \t]+(?P<message>.*)'
        lines = re.finditer(expression, report_data)

        for line in lines:
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': None,
                'column_end':   None,
                'message':      line.group('message'),
                'severity':     None,
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class CheckJavaScript(BaseChecker):
    def __init__(self):
        self.file_extension = 'js'

        self.errors_list = []

        self.linters = [
            JsHint(),
        ]


class JsHint(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out([
            'jshint',
            temp_file_path,
            '--config',
            '/home/ivan/projects/codestyle/checker/jshint.conf',
            '--reporter',
            '/home/ivan/projects/codestyle/checker/jshint_reporter.js']
        )

        return self.errors_list

    def parse_report(self, report_data):
        # данные уже приходят в JSON формате
        errors = json.loads(report_data)

        for error_info in errors:
            error = error_info.get('error', None)

            error_type = 'error' if error.get('id', None) == '(error)' else 'warning'

            if error.get('evidence', None):
                error_column_end = len(error.get('evidence', None)) - error.get('character', None)
            else:
                error_column_end = error.get('character', None)

            args = {
                'line_start':   error.get('line', None),
                'line_end':     error.get('line', None),
                'column_start': error.get('character', None),
                'column_end':   error_column_end,
                'message':      error.get('reason', None),
                'severity':     error_type,
                'type':         error.get('code', None)
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class CheckCss(BaseChecker):
    def __init__(self):
        self.file_extension = 'css'

        self.errors_list = []

        self.linters = [
            CssLint(),
            Recess()
        ]


class CssLint(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['csslint', '--format=compact', temp_file_path])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'.*:\s(line\s(?P<line>\d)+\,\scol\s(?P<column>\d)+\,\s)?(?P<severity>Warning|Error)\s\-\s(?P<message>.*)'
        lines = re.finditer(expression, report_data)

        for line in lines:
            severity = 'error' if line.group('severity') == 'Error' else 'warning'
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': line.group('column'),
                'column_end':   line.group('column'),
                'message':      line.group('message'),
                'severity':     severity,
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class CheckHtml(BaseChecker):
    def __init__(self):
        self.file_extension = 'html'

        self.errors_list = []

        self.linters = [
            HtmlTidy(),
        ]


class HtmlTidy(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['tidy', '-eq', temp_file_path])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'^line\s(?P<line>\d+)\scolumn\s(?P<column>\d)+\s-\s(?P<severity>Warning|Error):\s(?P<message>.+)'

        for row in report_data.splitlines():
            line = re.match(expression, row)

            if line:
                severity = 'error' if line.group('severity') == 'Error' else 'warning'
                args = {
                    'line_start':   line.group('line'),
                    'line_end':     line.group('line'),
                    'column_start': line.group('column'),
                    'column_end':   line.group('column'),
                    'message':      line.group('message'),
                    'severity':     severity,
                    'type':         None
                }

                error = CheckError(**args)
                self.errors_list.append(error)


class CheckPython(BaseChecker):
    def __init__(self):
        self.file_extension = 'py'

        self.errors_list = []

        self.linters = [
            Pep8(),
            PyFlakes(),
            PyLint()
        ]


class Pep8(BaseLinter):

    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        _errors_list = []

        class Pep8Report(pep8.BaseReport):
            def error(self, line_number, offset, text, check):
                error_type = text[:4]
                severity = 'error' if error_type.startswith('E') else 'warning'

                args = {
                    'line_start':   line_number,
                    'line_end':     line_number,
                    'column_start': offset,
                    'column_end':   offset,
                    'message':      text[5:],
                    'severity':     severity,
                    'type':         error_type
                }

                error = CheckError(**args)
                _errors_list.append(error)

                return error_type

        ignore = pep8.DEFAULT_IGNORE.split(',')

        options = pep8.StyleGuide(reporter=Pep8Report, ignore=ignore).options
        options.max_line_length = pep8.MAX_LINE_LENGTH

        pep8.Checker(filename=temp_file_path, lines=None, options=options).check_all()

        self.errors_list = _errors_list

        return self.errors_list

    def parse_report(self, report_data):
        pass


class PyFlakes(BaseLinter):

    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        try:
            tree = compile(code_source, temp_file_path, "exec", _ast.PyCF_ONLY_AST)
        except (SyntaxError, IndentationError), value:
            wrong_code = value.text.splitlines()[-1]

            args = {
                'line_start':   value.lineno,
                'line_end':     value.lineno,
                'column_start': value.offset,
                'column_end':   len(wrong_code) - value.offset,
                'message':      value.args[0],
                'severity':     'error',
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)
        except ValueError, e:
            args = {
                'line_start':   None,
                'line_end':     None,
                'column_start': None,
                'column_end':   None,
                'message':      e.args[0],
                'severity':     'error',
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)
        else:
            reports = pyflakes.Checker(tree, temp_file_path)

            for report in reports.messages:
                args = {
                    'line_start':   report.lineno,
                    'line_end':     report.lineno,
                    'column_start': None,
                    'column_end':   None,
                    'message':      report.message % report.message_args,
                    'severity':     'error',
                    'type':         None
                }

                error = CheckError(**args)
                self.errors_list.append(error)
        finally:
            return self.errors_list

    def parse_report(self, report_data):
        pass


class PyLint(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова
        ignored_list = ['F0401']
        ignored = ','.join([str(i) for i in ignored_list])

        self.shell_out([
            'pylint',
            '--reports=n',
            '--output-format=parseable',
            '--symbols=y',
            "--disable={0}".format(ignored),
            temp_file_path])

        return self.errors_list

    def parse_report(self, report_data):
        expression = r'.*\:(?P<line>\d)+\:\s\[(?P<type>.)+\,?.*\]\s(?P<message>.)*'
        lines = re.finditer(expression, report_data)

        for line in lines:
            severity = 'error' if line.group('type').startswith('E') else 'warning'
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': None,
                'column_end':   None,
                'message':      line.group('message'),
                'severity':     severity,
                'type':         line.group('type')
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class CheckLess(BaseChecker):
    def __init__(self):
        self.file_extension = 'less'

        self.errors_list = []

        self.linters = [
            LessJs(),
            Recess()
        ]


class Recess(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['recess', '--strictPropertyOrder=false', temp_file_path])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'\[36m(?P<message>.*)\x1b\[39m\s+.*\[90m\s+(?P<line>\d+)'
        lines = re.finditer(expression, report_data)

        for line in lines:
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': None,
                'column_end':   None,
                'message':      line.group('message'),
                'severity':     'error',
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)


class LessJs(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        self.shell_out(['lessc', '--no-color', temp_file_path])
        return self.errors_list

    def parse_report(self, report_data):
        expression = r'(?P<severity>.+)\:\s(?P<message>.+)\sin.*\:(?P<line>\d+)\:(?P<column>\d*)'
        lines = re.finditer(expression, report_data)

        for line in lines:
            severity = 'error' if line.group('severity') == 'ParseError' else 'warning'
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': line.group('column'),
                'column_end':   line.group('column'),
                'message':      line.group('message'),
                'severity':     severity,
                'type':         None
            }

            error = CheckError(**args)
            self.errors_list.append(error)


if __name__ == "__main__":
    content = open('/home/ivan/projects/codestyle/examples/phpcs.php', 'r').read()
    checker = CheckPhp()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[1].__dict__

    content = open('/home/ivan/projects/codestyle/examples/javascript.js', 'r').read()
    checker = CheckJavaScript()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[1].__dict__

    content = open('/home/ivan/projects/codestyle/examples/csslint.css', 'r').read()
    checker = CheckCss()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[1].__dict__
    print checker.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/examples/tidy.html', 'r').read()
    checker = CheckHtml()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[1].__dict__
    print checker.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/examples/python.py', 'r').read()
    checker = CheckPython()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[0].__dict__
    print checker.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/examples/less/style.less', 'r').read()
    checker = CheckLess()
    checker.check(content)
    print len(checker.errors_list)
    print checker.errors_list[0].__dict__
    print checker.errors_list[-1].__dict__
