# -*- encoding: utf-8 -*-

import json

class BaseException(Exception):

    code = None
    message = "Checker error"

    def __init__(self, message=None, params=None):
        if message:
            self.message = message

        if params:
            self.params = params

    def __str__(self):
        return "[{code}] {message}. Params: {params}".format(
            code=self.code, 
            message=self.message, 
            params=self.params
        )

    def get_error(self):
        return "{message}. Params: {params}".format(
            message=self.message, 
            params=self.params
        )


class LinterLookupException(BaseException):

    code = 510
    message = "Linter does not exist"