# -*- encoding: utf-8 -*-

import _ast

import pyflakes.checker as pyflakes

from .. base import BaseLinter
from .. errors import CheckError


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
