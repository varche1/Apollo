# -*- encoding: utf-8 -*-

import re
from .. base import BaseLinter
from .. errors import CheckError


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
