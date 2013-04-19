# -*- encoding: utf-8 -*-

import os
import json
from .. base import BaseLinter
from .. errors import CheckError


class JsHint(BaseLinter):
    def __init__(self):
        self.errors_list = []

    def lint(self, temp_file_path, code_source=None):
        """
        """
        # формирование аргументов вызова

        conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jshint.conf')
        reporter = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jshint_reporter.js')

        self.shell_out([
            'jshint',
            temp_file_path,
            '--config',
            conf,
            '--reporter',
            reporter]
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
