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

	def __init__(self, **params):
		self.__params = params

		self.status = Task.Statuses.NOT_STARTED
		self.handled = False
		self.result = None

		threading.Thread.__init__(self)

		logging.debug("Task: Init new task %s" % id(self))

	def run(self):
		self.status = Task.Statuses.RUNNING

		req = self.__prepareRequest()

		logging.debug("Task: Send request in task %s to url %s" % 
			(id(self), self.__params['url']))

		try:
			req_result = urllib.request.urlopen(req)

			logging.debug("Task: Get result in task %s" % id(self))

			result = req_result.read().decode('ascii')

			logging.debug("Task: Raw result for task %s ->\n%s" % 
				(id(result), result))

			self.result = json.loads(result)

			self.status = Task.Statuses.NORMAL_FINISH
		except urllib.error.URLError as e:
			self.status = Task.Statuses.URL_ERROR

			logging.debug("Task: Error '%s' in task %s" % 
				(e, id(self))
			)
		except urllib.error.HTTPError as e:
			self.status = Task.Statuses.HTTP_ERROR

			logging.debug("Task: Error '%s' in task %s" % 
				(e, id(self))
			)
		except Exception:
			self.status = Task.Statuses.UNKNOWN_ERROR

			logging.debug("Task: Unknown error in task %s" % id(self))

	def __prepareRequest(self):
		req = urllib.request.Request(self.__params['url'])
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)')

		data = {
			'language': self.__params['language'],
			'source': base64.b64encode(self.__params['source'].encode('ascii'))
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
				if task.status != Task.Statuses.RUNNING:
					if task.status == Task.Statuses.NOT_STARTED:
						logging.debug("TaskManager: Run task %s" % id(self))
						
						task.start()
					else:
						task.handled = True

						logging.debug("TaskManager: Task %s is finish" % id(self))
						
						finish_callback(task)

			self.__tasks = [task for task in self.__tasks if not task.handled]

			time.sleep(self.__options['interval'])

	def add(self, task):
		self.__tasks.append(task)

		logging.debug("TaskManager: New task %s was added in manager" % id(task))
