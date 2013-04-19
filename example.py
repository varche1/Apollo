# -*- encoding: utf-8 -*-

from checkers import CheckPhp, CheckJavaScript, CheckCss, CheckHtml, CheckPython, CheckLess

if __name__ == "__main__":
    content = open('/home/ivan/projects/codestyle/example_code/phpcs.php', 'r').read()
    checker_object = CheckPhp()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__

    content = open('/home/ivan/projects/codestyle/example_code/javascript.js', 'r').read()
    checker_object = CheckJavaScript()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__

    content = open('/home/ivan/projects/codestyle/example_code/csslint.css', 'r').read()
    checker_object = CheckCss()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/example_code/tidy.html', 'r').read()
    checker_object = CheckHtml()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[1].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/example_code/python.py', 'r').read()
    checker_object = CheckPython()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[0].__dict__
    print checker_object.errors_list[-1].__dict__

    content = open('/home/ivan/projects/codestyle/example_code/less/style.less', 'r').read()
    checker_object = CheckLess()
    checker_object.check(content)
    print len(checker_object.errors_list)
    print checker_object.errors_list[0].__dict__
    print checker_object.errors_list[-1].__dict__
