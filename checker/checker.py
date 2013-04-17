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

        self.severities_available = ['error', 'warning']

        # Линия начала ошибки
        self.line_start = kwargs.get('line_start', None)

        # Линия конца ошибки
        self.line_end = kwargs.get('line_end', None)

        # Колонка начала ошибки
        self.column_start = kwargs.get('column_start', None)

        # Колонка конца ошибки
        self.column_end = kwargs.get('column_end', None)

        # Суровость ошибки
        self.severity = kwargs.get('severity', self.severities_available[0])

        if not self.severity:
            self.severity = self.severities_available[0]

        if self.severity not in self.severities_available:
            exeption = "Wrong error severity: {severity}. Available types are: {types}".format(
                severity=self.type,
                types=self.severities_available)
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

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=info, cwd=home)

        if proc.stdout:
            data = proc.communicate()[0]
            self.parse_report(data)

        return data

    @abc.abstractmethod
    def lint(self, temp_file_path):
        """Метод реализующий проверку кода нужного файла на диске"""
        return

    @abc.abstractmethod
    def parse_report(self, report_data):
        """Метод реализующий парсинг ответа от низкоуровнего проверяльщика"""
        return


class BaseChecker(object):
    __metaclass__ = abc.ABCMeta

    def check(self, content):
        temp_file_name = "tmp-{random}.{ext}".format(ext=self.file_extension, random=str(uuid4()))
        temp_file_path = os.path.abspath(os.path.join(os.getcwd(), temp_file_name))

        try:
            with open(temp_file_path, "w") as f:
                f.write(content)

            for linter in self.linters:
                self.errors_list += linter.lint(temp_file_path)
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

    def lint(self, temp_file_path):
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

    def lint(self, temp_file_path):
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

    def lint(self, temp_file_path):
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
