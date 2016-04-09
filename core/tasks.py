from __future__ import absolute_import

import time

from celery import shared_task

@shared_task
def experimental(numbers):
    print "experiment occuring"
    time.sleep(30)
    return True

@shared_task
def update_cache():
    print "updating cache"
    time.sleep(30)
    return True


import logging
logging.basicConfig()
