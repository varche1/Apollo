# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import sys
import os.path
import json

from async.celery import celery

projects_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(projects_dir)

from checkers.checkers import CheckPhp, CheckJavaScript, CheckCss, CheckHtml, CheckPython, CheckLess

@celery.task
def check_code(language, source):
	checker = {
	    'python': CheckPython,
	    'php': CheckPhp,
	    'javascript': CheckJavaScript,
	    'css': CheckCss,
	    'less': CheckLess,
	    'html': CheckHtml,
	}.get(language)

	checker_object = checker()
	checker_object.check(source)

	return checker_object.get_errors_json()