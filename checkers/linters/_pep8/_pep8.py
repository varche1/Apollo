# -*- encoding: utf-8 -*-

import pep8

from .. base import BaseLinter
from .. errors import CheckError


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
