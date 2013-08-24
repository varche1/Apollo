# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import sys
import os.path
import json

from pymongo import MongoClient
from async.celery import celery

projects_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(projects_dir)

from checkers.checkers import CheckPhp, CheckJavaScript, CheckCss, CheckHtml, CheckPython, CheckLess

client = MongoClient()
db = client.apollo
collection = db.were_tested

def check_cache(hash_of_source):
    checked = collection.find_one({"hash_of_source": hash_of_source})

    if not checked:
        return None

    return checked["errors"]

def add_to_cache(errors, hash_of_source, language, source):
    fields = {
        "errors": errors,
        "hash_of_source": hash_of_source,
        "language": language,
        "source": source
    }

    collection.insert(fields)

def get_checker(language):
    checker = {
        'python': CheckPython,
        'php': CheckPhp,
        'javascript': CheckJavaScript,
        'css': CheckCss,
        'less': CheckLess,
        'html': CheckHtml,
    }.get(language)

    return checker()

@celery.task
def check_code(language, source):
    hash_of_source = hash((language, source))
    errors = check_cache(hash_of_source)
    if errors:
        return errors
    else:
        checker = get_checker(language)
        checker.check(source)

        errors = checker.get_errors_json()
        add_to_cache(errors, hash_of_source, language, source)

        return errors