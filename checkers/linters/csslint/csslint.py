# -*- encoding: utf-8 -*-

import re
from .. base import BaseLinter
from .. errors import CheckError


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
