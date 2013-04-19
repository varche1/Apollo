# -*- encoding: utf-8 -*-

import re
from .. base import BaseLinter
from .. errors import CheckError


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
