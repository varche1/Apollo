# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import sys
import os.path
import json

import tornado.ioloop
import tornado.websocket
import tornado.web

from async.tasks import check_code

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        request = json.loads(message)

        result = check_code.delay(request)

        print(result)

        # self.write_message(checker_object.errors_list[1].__dict__)
        self.write_message(result.get())

    def on_close(self):
        print("WebSocket closed")

application = tornado.web.Application([
    (r"/ws", EchoWebSocket)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()