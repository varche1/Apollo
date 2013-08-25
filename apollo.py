# -*- coding: utf-8 -*-

from .plugin.core import Apollo, ApolloEvents, ApolloCommand

# Init plugin
plugin = Apollo()

def plugin_loaded():
    plugin.load()

# Events 
class ApolloEventsListener(ApolloEvents):
    def on_post_save(self, view):
        settings = plugin.get_settings()
        
        if settings and settings.get('apollo_check_after_save'):
            plugin.check(view)

    # def on_activated(self, view):
    # 	plugin.show_errors(view)

# Commands
# =======================================
# Run check
class ApolloCheckCommand(ApolloCommand):
    def run(self, edit):
        plugin.check(self.view)
