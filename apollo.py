# -*- coding: utf-8 -*-

from .plugin.core import Apollo, ApolloCommand

# Init plugin
plugin = Apollo()

# Plugin full load event
def plugin_loaded():
    plugin.load()


# Commands

# Run check
class ApolloCheckCommand(ApolloCommand):
    def run(self, edit):
        plugin.check(self.view)
