from __future__ import absolute_import

from celery import shared_task

from time import sleep
from celery import task, current_task
from monitor.monitor import MonitorThread

@shared_task
def do_work():
    """ Get some rest, asynchronously, and update the state all the time """
    for i in range(12):
        sleep(1)
    MonitorThread.update_jobs_state(do_work.request.id, do_work, 'DO_WORK', 25, 100)
    print 'calling second'
    second_step()
    print 'calling third'
    third_step()
    forth_step()

        # print 'current ', i
        # do_work.update_state(state='HALLOOO', meta={'current': i, 'total': 20})
        # if i == 6:
        #     r_except()
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


def r_except():
    #raise ValueError("Shii")
    r = 2 / 0.0

def second_step():
    for i in range(6):
        sleep(2)
    print "in second"
    print "request id ", do_work.request.id
    MonitorThread.update_jobs_state(do_work.request.id, do_work, 'SEC_STEP', 40, 100)


def third_step():
    for i in range(7):
        sleep(2)
    print "in third"
    print "request id ", do_work.request.id

    MonitorThread.update_jobs_state(do_work.request.id, do_work, 'THIRD_STEP', 80, 100)

def forth_step():
    for i in range(2):
        sleep(2)
    print "in forth"
    print "request id ", do_work.request.id
    MonitorThread.update_jobs_state(do_work.request.id, do_work, 'FORTH_STEP', 100, 100)

