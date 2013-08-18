# -*- encoding: utf-8 -*-

import sys
import os.path
import json

import tornado.ioloop
import tornado.websocket
import tornado.web

projects_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(projects_dir)

from checkers_codestylelinter.checkers import CheckPhp, CheckJavaScript, CheckCss, CheckHtml, CheckPython, CheckLess

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        request = json.loads(message)

        checker = {
            'python': CheckPython,
            'php': CheckPhp,
            'javascript': CheckJavaScript,
            'css': CheckCss,
            'less': CheckLess,
            'html': CheckHtml,
        }.get(request['language'])

        checker_object = checker()
        checker_object.check(request['source'].encode('utf-8'))

        self.write_message(checker_object.errors_list[1].__dict__)

    def on_close(self):
        print("WebSocket closed")

application = tornado.web.Application([
    (r"/ws", EchoWebSocket)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()