# -*- coding: utf-8 -*-

from .libs import requests

import os

import sublime
import sublime_plugin

class Apollo:
    def __init__(self):
        self.results = {}

    def load(self):
        self.settings = sublime.load_settings('apollo.sublime-settings')

        if (self.settings.get('debug')):
            print("Apollo init finish!")

class ApolloCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass  # Not implemented