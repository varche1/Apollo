# -*- encoding: utf-8 -*-

import json

class CheckerResponse(object):

    status = None
    code = None
    message = None
    data = None

    OK_STATUS = True
    ERROR_STATUS = False

    OK_CODE = 200

    def __init__(self, status=OK_STATUS, code=OK_CODE, message=None, data=None, *args, **kwargs):
        self.status = status
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        fileds = {
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }

        return fileds

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.to_json()