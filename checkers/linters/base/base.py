# -*- encoding: utf-8 -*-

import abc
import subprocess
from os.path import expanduser


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
