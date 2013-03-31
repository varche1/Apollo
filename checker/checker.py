# -*- encoding: utf-8 -*-

import os
import re
import subprocess
from functools import wraps
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


        # Линия начала ошибки
        if 'line_start' in kwargs.keys():
            self.line_start = kwargs['line_start']

        # Линия конца ошибки
        if 'line_end' in kwargs.keys():
            self.line_end = kwargs['line_end']

        # Колонка начала ошибки
        if 'column_start' in kwargs.keys():
            self.column_start = kwargs['column_start']

        # Колонка конца ошибки
        if 'column_end' in kwargs.keys():
            self.column_end = kwargs['column_end']

        # Сообщение ошибки
        if 'severity' in kwargs.keys():
            self.severity = kwargs['severity']

        # Суровость ошибки
        if 'message' in kwargs.keys():
            self.message = kwargs['message']

        # Тип ошибки
        if 'type' in kwargs.keys():
            self.type = kwargs['type']


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

    def lint(self, content):
        with open(self.temp_file, "w") as f:
            f.write(content)
            
        return self._lint()
        os.remove(self.temp_file)

    def _shell_out(self, cmd):
        data = None
        info = None
        home = expanduser("~")

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=info, cwd=home)

        if proc.stdout:
            data = proc.communicate()[0]
            self._parse_report(data)

        return data
    
    @abc.abstractmethod
    def _lint(self):
        """Метод реализующий получение ответа от низкоуровнего проверяльщика"""
        return

    @abc.abstractmethod
    def _parse_report(self, report_data):
        """Метод реализующий парсинг ответа от низкоуровнего проверяльщика"""
        return

class CheckPhp():
    def __init__(self):
        self.errors_list = []

    def check(self, content):
        """
        """
        self.errors_list = PhpCodeSniffer().lint(content)

class PhpCodeSniffer(BaseLinter):
    def __init__(self):
        self.file_extension = 'php'
        self.temp_file = os.path.abspath(os.path.join(os.getcwd(), "temp_file_to_check.{ext}".format(ext=self.file_extension)))
        self.errors_list = []

    def _lint(self):
        """
        """
        # формирование аргументов вызова

        self._shell_out(['phpcs', '--report=checkstyle', self.temp_file])
        return self.errors_list

    def _parse_report(self, report_data):
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


if __name__ == "__main__":
    content = open('/home/www/checker.codestyle.dev.webpp.ru/docs/codestyle/examples/phpcs.php', 'r').read()
    checker = CheckPhp()
    checker.check(content)
    print len(checker.errors_list)

    # c = "echo \"{0}\" >  e.php".format(content)

    # c = "echo \"hello\" >  e.php"

    # print c

    # p = subprocess.Popen([c], stdout=subprocess.PIPE)

    # if p.stdout:
    #     data = p.communicate()[0]
    #     print data

    # content = open('/home/www/checker.codestyle.dev.webpp.ru/docs/codestyle/examples/phpcs.php', 'r').read()
    # checker = CheckPhp()
    # checker.check(content)
    # print len(checker.errors_list)