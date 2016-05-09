from __future__ import absolute_import

import logging
import os
from pprint import pprint
import collections
# from .singleton import Singleton
from celery.task.control import inspect
import datetime
from apscheduler.schedulers.background import BackgroundScheduler


logger = logging.getLogger(__name__)

class ScreenShot(object):

    def __init__(self, mode='r', interval=10):
        """
        :param mode: either 'r'(realtime) , or 'p' (periodic)
        :param interval: in seconds, default is 10. Only has
            effect in 'p' mode. Will ask the broker if there are
            new events to be registered.

        Maybe call the _get* methods in an endless loop
        every couple of seconds instead of explicitly
        ``set_has_been_updated``

        registered
        {u'celery@larss-MacBook-Pro.local': [u'task_progress.celery.debug_task',
          u'tasks.add',
          u'tasks.do_work',
          u'tasks.mul',
          u'tasks.xsum']}

        """
        self.mode = mode.lower()
        if self.mode not in ('r', 'p'):
            raise AttributeError(
                "[-] Mode must either be 'p' or 'r'")
        self.set_inspect()

        self.register_dict = self._get_registered_jobs()
        self.active_dict = None
        self.has_been_updated = False

        if self.mode == 'p':
            self.sched = BackgroundScheduler()
            self.sched.add_job(self._refresh_active_jobs, 'interval', seconds=interval)
            self.sched.start()

    def shutdown(self):
        self.sched.shutdown(wait=False)

    def set_has_been_updated(self):
        """
        tell the object that a new job has
        been started
        :return:
        """
        self.has_been_updated = True
        logger.info("[+] has_been_updated == {0}".format(self.has_been_updated))

    def update_has_been_published(self):
        """
        tell the object that a new job has
        been published
        :return:
        """
        self.has_been_updated = False
        logger.info(
            "[+] Screenshot has been published. "
            "has_been_updated == {0}".format(self.has_been_updated))

    def set_inspect(self):
        self.inspect = inspect()


    def _get_registered_jobs(self):
        """
        :return: dict of registered tasks
        """
        return self.inspect.registered()

    def _refresh_active_jobs(self):
        """
        :return: dict of active tasks
        """
        self.active_dict = self.inspect.active()
        # print "refreshed..."
        # print "now active: ", self.active_dict


    def _get_queue(self):
        return self.inspect.reserved()

    def list_registered_tasks(self, pprint_list=False):
        """
        """
        if pprint_list:
            for items in self.register_dict.itervalues():
                pprint(items, indent=4)
        return self.register_dict.values()


    def list_jobs_in_queue(self, pprint_list=False):
        queue = self._get_queue()

        if not queue:
            logger.info("No jobs in the queue at the moment")
            print "No jobs in the queue at the moment"
            return

        if pprint_list:
            for items in queue.itervalues():
                pprint(items, indent=4)
        return queue.values()


    def list_running_jobs(self, sort_by="", pprint_list=False):
        self._refresh_active_jobs()
        if not self.active_dict.values()[0]:
            logger.info("No running jobs at the moment")
            print "No running jobs at the moment"
            return

        jobs = []
        for outer_list in self.active_dict.itervalues():
            for inner_dict in outer_list:
                if pprint_list:
                    pprint(inner_dict, indent=4)
                jobs.append(inner_dict)
        return jobs

    def get_running_job(self, job_id):
        """
        http://stackoverflow.com/questions/20091505/celery-task-with-a-time-start-attribute-in-1970
        default key = 'id'
        options:
            - task name
            - worker_pid
            - hostname
        """
        JobDescription = collections.namedtuple(
            "JobDescription", 'id, kwargs, time_start, name'
        )
        self._refresh_active_jobs()
        if not self.active_dict.values()[0]:
            logger.info("No running jobs at the moment")
            print "No running jobs at the moment"
            return

        for outer_list in self.active_dict.itervalues():
            for inner_dict in outer_list:
                if job_id in inner_dict.values():
                    # datetime.datetime.fromtimestamp(146788.32347280602).strftime('%Y-%m-%d %H:%M:%S')
                    values = [inner_dict.get(field) for field in JobDescription._fields]
                    return JobDescription(*values)


# def is_empty(seq):
#     try:
#         return all(empty(x) for x in seq)
#     except TypeError:
#         return False
#
#
#
#
#
# i.active()
# active = {u'celery@larss-MacBook-Pro.local': [{u'acknowledged': True,
#    u'args': u'[]',
#    u'delivery_info': {u'exchange': u'celery',
#     u'priority': 0,
#     u'redelivered': None,
#     u'routing_key': u'celery'},
#    u'hostname': u'celery@larss-MacBook-Pro.local',
#    u'id': u'my-bad-ass',
#    u'kwargs': u'{}',
#    u'name': u'tasks.do_work',
#    u'time_start': 146788.32347280602,
#    u'worker_pid': 9388}]}
#
#
#
# @Singleton
# class Foo:
#    def __init__(self):
#        print 'Foo created'
#
# f = Foo() # Error, this isn't how you get the instance of a singleton
#
# f = Foo.Instance() # Good. Being explicit is in line with the Python Zen
# g = Foo.Instance() # Returns already created instance
#
# print f is g # True

import threading
import time
from celery import Celery
import logging
import os
from pprint import pprint
import collections
# from .singleton import Singleton
from celery.task.control import inspect
import datetime
from apscheduler.schedulers.background import BackgroundScheduler


class MonitorThread(object):
    #! TODO: You need to set CELERY_SEND_EVENTS flag as true in your celery config
    def __init__(self, celery_app, interval=1):
        self.celery_app = celery_app
        self.interval = interval
        self.set_inspect()


        self.state = self.celery_app.events.State()

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def catchall(self, event):
        if event['type'] != 'worker-heartbeat':
            self.state.event(event)
            print self.state.event


        if event['type'] == 'task-started':
            self._refresh_active_jobs()


    def set_inspect(self):
        self.inspect = inspect()

    def _refresh_active_jobs(self):
        """
        :return: dict of active tasks
        """
        self.active_dict = self.inspect.active()
        print "refreshed..."
        print "now active: ", self.active_dict

    def run(self):
        while True:
            try:
                with self.celery_app.connection() as connection:
                    recv = self.celery_app.events.Receiver(connection, handlers={
                        '*': self.catchall
                    })
                    recv.capture(limit=None, timeout=None, wakeup=True)

            except (KeyboardInterrupt, SystemExit):
                raise

            except Exception:
                # unable to capture
                pass

            time.sleep(self.interval)

if __name__ == '__main__':
    app = Celery(broker='redis://localhost:6379/0')
    MonitorThread(app)
    app.start()