# -*- encoding: utf-8 -*-

import json

from linters.errors import CheckError


class ErrorsManager(list):

    def __add__(self, rhs):
        if not isinstance(rhs, CheckError):
            raise Exception("Can not append none 'CheckError' isinstance to errors list.")

        return ErrorsManager(list.__add__(self, rhs))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        try:
            return ErrorsManager(result)
        except TypeError:
            return result

    def get_sorted(self):
        def cmp(item_1, item_2):
            if item_1.severity == "error" and item_2.severity == "warning":
                return -1
            elif item_1.severity == "warning" and item_2.severity == "error":
                return 1
            elif item_1.severity == item_2.severity:
                if item_1.line_start < item_2.line_start:
                    return -1
                elif item_1.line_start > item_2.line_start:
                    return 1
                else:
                    return 0

        return sorted(self, cmp)

    def get_errors(self):
        sorted_errors = self.get_sorted()
        return [error.get_error() for error in sorted_errors]
