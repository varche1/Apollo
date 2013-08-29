# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import sys
import os.path
import json
import base64

import tornado.ioloop
import tornado.web
import tornado.gen
import tcelery

from async.tasks import check_code
from server_response import ServerResponse as Response

tcelery.setup_nonblocking_producer()

class CheckCodeHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        language = self.get_argument('language', None)
        source = base64.b64decode(self.get_argument('source', "")).decode('utf-8')

        task_result = yield tornado.gen.Task(check_code.apply_async, args=[language, source])
        response = Response(**task_result.result.to_dict())

        self.write(str(response))
        self.finish()

application = tornado.web.Application([
    (r"/check_code", CheckCodeHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()