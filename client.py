# -*- encoding: utf-8 -*-

import websocket
import thread
import json

import sys
import os.path

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(language, file_name):
        content = open(os.path.join(example_dir, file_name), 'r').read()
        message = {
            'language': language,
            'source': content
        }
        ws.send(json.dumps(message))

    thread.start_new_thread(run, ('php', 'phpcs.php'))
    thread.start_new_thread(run, ('javascript', 'javascript.js'))
    thread.start_new_thread(run, ('css', 'csslint.css'))
    thread.start_new_thread(run, ('html', 'tidy.html'))
    thread.start_new_thread(run, ('python', 'python.py'))
    thread.start_new_thread(run, ('less', 'less/style.less'))


if __name__ == "__main__":
    projects_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    example_dir = os.path.join(projects_dir, 'checkers_codestylelinter', 'example_code')

    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()