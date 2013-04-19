# -*- encoding: utf-8 -*-

import re
from .. base import BaseLinter
from .. errors import CheckError


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
