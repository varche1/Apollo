# -*- encoding: utf-8 -*-

import os

from checkers import CheckPhp, CheckJavaScript, CheckCss, CheckHtml, CheckPython, CheckLess

if __name__ == "__main__":
    example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example_code')

    content = open(os.path.join(example_dir, 'phpcs.php'), 'r').read()
    checker_object = CheckPhp()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__

    content = open(os.path.join(example_dir, 'javascript.js'), 'r').read()
    checker_object = CheckJavaScript()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__

    content = open(os.path.join(example_dir, 'csslint.css'), 'r').read()
    checker_object = CheckCss()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open(os.path.join(example_dir, 'tidy.html'), 'r').read()
    checker_object = CheckHtml()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open(os.path.join(example_dir, 'python.py'), 'r').read()
    checker_object = CheckPython()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[0].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open(os.path.join(example_dir, 'less/style.less'), 'r').read()
    checker_object = CheckLess()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[0].__dict__
    print checker_object.errors_list[-1].__dict__
