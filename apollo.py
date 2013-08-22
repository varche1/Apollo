# -*- coding: utf-8 -*-

from .plugin.core import Apollo, ApolloCommand

# Init plugin
plugin = Apollo()


# Commands
class ApolloTestCommand(ApolloCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Apollo test")


# Plugin full load event
def plugin_loaded():
    plugin.load()