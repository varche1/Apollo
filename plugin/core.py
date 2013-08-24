# -*- coding: utf-8 -*-s

import os
import logging

import sublime
import sublime_plugin

from .tasks import Task, TaskManager


class Apollo:
    def __init__(self):
        self.queue = TaskManager()
        self.results = {}

    def load(self):
        self.settings = sublime.load_settings('apollo.sublime-settings')
        if self.settings.get("debug"):
            logging.basicConfig(level="DEBUG")

        self.queue.init(
            interval=self.settings.get('manager_interval') / 1000, 
            on_task_finish=self.on_task_finish
        )
        self.queue.start() # Run queue in tread

        logging.debug("Apollo init finish!")

    def check(self, view):
        syntax = view.settings().get('syntax')
        if syntax:
            syntax_parts = syntax.split("/")
            language = syntax_parts[1].lower()

            source = body = view.substr(sublime.Region(0, view.size()))

            task = Task(
                url=self.settings.get('backend_url'),
                view_id=view.id(),
                language=language,
                source=source
            )

            self.queue.add(task)
        else:
            logging.info("File has not correct syntax")

    def on_task_finish(self, task):
        pass


class ApolloMessage():
    def __init__(self, arg):
        pass
        

class ApolloCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass  # Not implemented
