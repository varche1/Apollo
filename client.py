# -*- encoding: utf-8 -*-

import sys
import os.path
import urllib
import urllib2
import base64
import json

def get_data(language, file_name):
    content = open(os.path.join(example_dir, file_name), 'r').read()
    data = {
        'language': language,
        'source': base64.b64encode(content)
    }

    return data

def make_request(values, url):
    headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())


if __name__ == "__main__":
    projects_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    example_dir = os.path.join(projects_dir, 'checkers', 'example_code')

    to_check = [
        ('php', 'phpcs.php'),
        ('javascript', 'javascript.js'),
        ('css', 'csslint.css'),
        ('html', 'tidy.html'),
        ('python', 'python.py'),
        ('less', 'less/style.less'),
        ('hiphop', 'phpcs.php'),
    ]

    for item in to_check:
        values = get_data(item[0], item[1])
        print(make_request(values, "http://do.fiveb.pw:8888/check_code"))
