# -*- encoding: utf-8 -*-

import os
import abc
from uuid import uuid4
import json

from errors_manager import ErrorsManager
from linters import PhpCodeSniffer
from linters import PhpMessDetector
from linters import JsHint
from linters import CssLint
from linters import Recess
from linters import HtmlTidy
from linters import Pep8
from linters import PyFlakes
from linters import PyLint
from linters import Less


class BaseChecker(object):
    __metaclass__ = abc.ABCMeta

    errors = ErrorsManager()

    def check(self, content):
        temp_file_name = "tmp-{random}.{ext}".format(ext=self.file_extension, random=str(uuid4()))
        temp_file_path = os.path.abspath(os.path.join(os.getcwd(), temp_file_name))

        try:
            with open(temp_file_path, "w") as f:
                f.write(content.encode("utf-8"))

            for linter in self.linters:
                self.errors += linter.lint(temp_file_path, content)
        finally:
            os.remove(temp_file_path)

    def get_errors_json(self):
        return self.errors.get_errors_json()



class CheckPhp(BaseChecker):
    def __init__(self):
        self.file_extension = 'php'

        self.linters = [
            PhpCodeSniffer(),
            PhpMessDetector()
        ]


class CheckJavaScript(BaseChecker):
    def __init__(self):
        self.file_extension = 'js'

        self.linters = [
            JsHint(),
        ]


class CheckCss(BaseChecker):
    def __init__(self):
        self.file_extension = 'css'

        self.linters = [
            CssLint(),
            Recess()
        ]


class CheckHtml(BaseChecker):
    def __init__(self):
        self.file_extension = 'html'

        self.linters = [
            HtmlTidy(),
        ]


class CheckPython(BaseChecker):
    def __init__(self):
        self.file_extension = 'py'

        self.linters = [
            Pep8(),
            PyFlakes(),
            PyLint()
        ]


class CheckLess(BaseChecker):
    def __init__(self):
        self.file_extension = 'less'

        self.linters = [
            Less(),
            Recess()
        ]
