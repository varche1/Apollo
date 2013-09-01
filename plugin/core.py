# -*- coding: utf-8 -*-

import os
import logging

import sublime
import sublime_plugin

from .tasks import Task, TaskManager


class Apollo():
    def __init__(self):
        self.__queue = TaskManager()
        self.__settings = None
        self.__messenger = None

    def load(self):
        self.__settings = sublime.load_settings('apollo.sublime-settings')
        if self.__settings.get("apollo_debug"):
            logging.basicConfig(level="DEBUG")

        self.__messenger = ApolloMessager(self.__settings)

        self.__queue.init(
            interval=self.__settings.get('apollo_manager_interval') / 1000,
            on_task_finish=self.__on_task_finish
        )
        self.__queue.start()  # Run queue in tread

        logging.debug("Apollo init finish!")

    def check(self, view):
        syntax = view.settings().get('syntax')
        if syntax:
            syntax_parts = syntax.split("/")
            language = syntax_parts[1].lower()

            source = view.substr(sublime.Region(0, view.size()))

            task = Task(
                url=self.__settings.get('apollo_backend_url'),
                view_id=view.id(),
                language=language,
                source=source
            )

            self.__queue.add(task)
        else:
            logging.debug("Apollo: File has not correct syntax")
            sublime.status_message("Apollo: File has not correct syntax")

    def get_settings(self):
        return self.__settings

    def show_errors(self, view):
        self.__messenger.show(str(view.id()))

    def __on_task_finish(self, task):
        if task.get_status() == Task.Statuses.NORMAL_FINISH:
            result = task.get_result()

            if result['status'] and result['code'] == Task.ResultCodes.OK:
                self.__messenger.schedule(
                    str(task.get_option('view_id')),
                    result['data'],
                    True
                )
            elif result['code'] == Task.ResultCodes.NO_LINTER:
                sublime.status_message(
                "Apollo: Check failed, backend don't have valid linter!"
            )
            else:
                sublime.status_message(
                "Apollo: Check failed, info: %s" % result['message']
            )
        else:
            sublime.status_message(
                "Apollo: Check failed, if you want get more info, enable debug mode and see console"
            )


class ApolloMessager():
    def __init__(self, settings):
        self.__panel_show_on = None
        self.__panel_visible = False

        self.__data = {}
        self.__settings = settings

    def schedule(self, view_id, lines, show_now):
        self.__data[view_id] = lines

        if show_now:
            self.show(view_id)

    def show(self, view_id):
        window = sublime.active_window()

        if self.__panel_visible:
            window.run_command('hide_overlay')

        if view_id in self.__data:
            view = window.active_view()

            errors_list = self.__data[view_id]
            
            list_for_show = []
            regions = []
            for record in errors_list:
                line_content = view.substr(view.full_line(view.text_point(record['line_start'], 0))).strip()

                list_for_show.append([
                    "[{severity}]{type}: {message}".format(
                        severity=record['severity'].upper(),
                        type=(" %s" % record['type']) if record['type'] else "",
                        message=record['message'],
                    ),
                    "{line}: {line_content}".format(
                        line=record['line_start'],
                        line_content=line_content,
                    )
                ])
                pt = view.text_point(record['line_start'] - 1, 0)
                region_line = view.line(pt)

                regions.append(region_line)

            window.show_quick_panel(list_for_show, self.__on_quick_panel_done)

            self.__panel_visible = True

            icon = 'dot' if self.__settings.get('apollo_show_marks') else ''
            outline = sublime.DRAW_OUTLINED if self.__settings.get('apollo_outline_errors') else sublime.HIDDEN
            if self.__settings.get('apollo_show_marks') or self.__settings.get('apollo_outline_errors'):
                view.add_regions(
                    "errors_%s" % view_id, regions, "string", icon, outline
                )
        else:
            if self.__panel_visible:
                window.run_command('hide_overlay')
                self.__panel_visible = False

    def __on_quick_panel_done(self, picked):
        self.__panel_visible = False

        if picked == -1:
            return

        window = sublime.active_window()
        view_id = window.active_view().id()
        if window.active_view().id() != int(view_id):
            return

        error = self.__data[str(view_id)][picked]

        pt = window.active_view().text_point(error['line_start'] - 1, 0)

        window.active_view().sel().clear()
        window.active_view().sel().add(sublime.Region(pt))
        window.active_view().show(pt)


class ApolloEvents(sublime_plugin.EventListener):
    pass  # Not implemented

class ApolloCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass  # Not implemented
