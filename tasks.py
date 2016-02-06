from __future__ import absolute_import

from celery import shared_task

from time import sleep
from celery import task, current_task


@shared_task
def do_work():
    """ Get some rest, asynchronously, and update the state all the time """
    for i in range(20):
        sleep(1)
        print 'current ', i
        print do_work.update_state(state='HALLOOO', meta={'current': i, 'total': 20})
        # current_task.update_state(state='PROGRESS',
        #     meta={'current': i, 'total': 100})

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)