# -*- encoding: utf-8 -*-

from __future__ import absolute_import

from celery import Celery

celery = Celery('async.celery',
                broker='amqp://guest:guest@localhost:5672//',
                backend='mongodb://localhost:27017/celery',
                include=['async.tasks'])

if __name__ == '__main__':
    celery.start()