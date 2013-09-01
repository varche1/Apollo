# -*- coding: utf-8 -*-s

import os
import urllib.request
import urllib.error
import json
import base64
import logging

import time
import threading

from .utils import enum

class Task(threading.Thread):
    Statuses = enum(
        NOT_STARTED=-1, 
        RUNNING=1, 
        NORMAL_FINISH=0, 
        UNKNOWN_ERROR=10,
        URL_ERROR=11,
        HTTP_ERROR=12,
    )

    ResultCodes = enum(
        OK=200,
        NO_LINTER=510,
    )

    def __init__(self, **params):
        self.__params = params
        
        self.__status = Task.Statuses.NOT_STARTED
        self.__result = None

        threading.Thread.__init__(self)

        logging.debug("Task: Init new task %s" % id(self))

    def run(self):
        self.__status = Task.Statuses.RUNNING

        req = self.__prepareRequest()

        logging.debug("Task: Send request in task %s to url %s" % 
            (id(self), self.__params['url']))

        try:
            req_result = urllib.request.urlopen(req)

            logging.debug("Task: Get result in task %s" % id(self))

            result = req_result.read().decode('ascii')

            logging.debug("Task: Raw result for task %s ->\n%s" % 
                (id(result), result))

            self.__result = json.loads(result)

            self.__status = Task.Statuses.NORMAL_FINISH
        except urllib.error.URLError as e:
            self.__status = Task.Statuses.URL_ERROR

            logging.debug("Task: Error '%s' in task %s" % 
                (e, id(self))
            )
        except urllib.error.HTTPError as e:
            self.__status = Task.Statuses.HTTP_ERROR
            logging.debug("Task: Error '%s' in task %s" % 
                (e, id(self))
            )
        except Exception:
            self.__status = Task.Statuses.UNKNOWN_ERROR

            logging.debug("Task: Unknown error in task %s" % id(self))

    def is_finish(self):
        if (self.__status == Task.Statuses.NOT_STARTED or
            self.__status == Task.Statuses.RUNNING):
            return False
        else:
            return True

    def get_status(self):
        return self.__status

    def get_result(self):
        return self.__result

    def get_option(self, option):
        if option in self.__params:
            return self.__params[option]
        else:
            return None

    def __prepareRequest(self):
        req = urllib.request.Request(self.__params['url'])
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)')

        data = {
            'language': self.__params['language'],
            'source': base64.b64encode(self.__params['source'].encode('utf-8'))
        }

        req.add_data(urllib.parse.urlencode(data).encode('ascii'))

        return req


class TaskManager(threading.Thread):
    def __init__(self):
        self.__tasks = {}

        threading.Thread.__init__(self)

    def init(self, **options):
        self.__options = options

    def run(self):
        finish_callback = self.__options['on_task_finish']

        while (True):
            for task in self.__tasks:
                if task.get_status() != Task.Statuses.RUNNING:
                    if task.get_status() == Task.Statuses.NOT_STARTED:
                        logging.debug("TaskManager: Run task %s" % id(self))
                        
                        task.start()
                    else:
                        logging.debug("TaskManager: Task %s is finish" % id(self))
                        
                        finish_callback(task)

            self.__tasks = [
                task for task in self.__tasks 
                    if not task.is_finish()
            ]

            time.sleep(self.__options['interval'])

    def add(self, task):
        self.__tasks.append(task)

        logging.debug("TaskManager: New task %s was added in manager" % id(task))
