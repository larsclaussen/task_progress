from __future__ import absolute_import

from celery.task.control import inspect
import threading
import time
import datetime
from celery import Celery
from pprint import pprint
from task_progress.celery import app
from celery.result import AsyncResult

class MonitorThread(object):
    #! TODO: You need to set CELERY_SEND_EVENTS flag as true in your celery config

    def __init__(self, celery_app, interval=1):
        self.celery_app = celery_app
        self.interval = interval
        self.set_inspect()
        self.start_time_dict = {}
        self.status_dict = {}

        self.active_dict = {}
        self.register_dict = {}
        self.queue_dict = {}
        self.jobs_done = []
        self._last_seen_uuid = None
        self.active_been_updated = False

        self.state = self.celery_app.events.State()

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def set_inspect(self):
        self.inspect = inspect()


    def list_registered_jobs(self, pprint_list=False):
        """
        """

        if not self.register_dict:
            self._refresh_registered_jobs()

        print "self.register_dict ", self.register_dict
        registered = []
        if self.register_dict:
            for outer_list in self.register_dict.itervalues():
                for inner_list in outer_list:
                    if pprint_list:
                        pprint(inner_list, indent=4)
                    registered.append(inner_list)
            return registered

    def list_running_jobs(self, sort_by="", pprint_list=False):
        if not self.active_dict or not self.active_dict.values()[0]:
            # logger.info("No running jobs at the moment")
            print "No running jobs at the moment"
            return

        jobs = []
        for outer_list in self.active_dict.itervalues():
            for inner_dict in outer_list:
                job_id = inner_dict['id']
                # call AsyncResult here with job id
                job = AsyncResult(job_id)
                if job.result is None:
                    pass
                else:
                    self.status_dict[job_id] = job.result
                inner_dict['status'] = self.status_dict.get(job_id) or None
                inner_dict['state'] = job.state
                inner_dict['start_time'] = self.start_time_dict.get(job_id) or None
                if pprint_list:
                    pprint(inner_dict, indent=4)
                jobs.append(inner_dict)
        return jobs

    @staticmethod
    def update_jobs_state(job_id, job_instance, state_name, step, total_steps):
        job_instance.update_state(task_id=job_id, state=state_name, meta={'current': step, 'total': total_steps})


    def list_jobs_in_queue(self, pprint_list=False):


        if self.queue_dict is None or not self.queue_dict.values()[0]:
            # logger.info("No jobs in the queue at the moment")
            print "No jobs in the queue at the moment"
            return

        if pprint_list:
            for items in self.queue_dict.itervalues():
                pprint(items, indent=4)
        return self.queue_dict.values()

    def _refresh_queue_info(self, _):
        print 'refreshing queue'
        self.queue_dict = self.inspect.reserved()
        print 'queue: ', self.queue_dict

    def _refresh_active_jobs(self, event=None):
        """
        :return: dict of active tasks
        """
        self.active_dict = self.inspect.active()
        print "############# event ", event
        if event:
            id = event[u'uuid']

            start_time = datetime.datetime.fromtimestamp(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            self.start_time_dict = {id: start_time}
            # self._add_start_time_to_active_dict(id, start_time)
        print "refreshed..."

    # def _add_start_time_to_active_dict(self, id, start_time):
    #     for outer_list in self.active_dict.itervalues():
    #         for inner_dict in outer_list:
    #             print "-------------", inner_dict
    #             if inner_dict['id'] == id:
    #                 inner_dict['start_time'] = start_time
    #                 print "^^^^^^^^^^^^^^^^^^inner updated! ", inner_dict
    #                 return


    def _update_jobs_done(self, event):
        print 'yeah!!!!!!!!***************'
        self.jobs_done.append(event)
        print self.jobs_done
        self._refresh_active_jobs(event)

    def _refresh_registered_jobs(self):
        """
        :return: dict of registered tasks
        """
        self.register_dict = self.inspect.registered()

    def run(self):
        while True:
            try:
                with self.celery_app.connection() as connection:
                    recv = self.celery_app.events.Receiver(
                        connection,
                         handlers={'task-failed': self._update_jobs_done,
                                   'task-succeeded': self._update_jobs_done,
                                   'task-sent' : self._refresh_queue_info,
                                   'task-received': self._refresh_queue_info,
                                   # 'task-revoked' : on_event,
                                   'task-started': self._refresh_active_jobs,
                                   # OR: '*' : on_event
                                   })

                    #     handlers={
                    #         '*': self.catchall, 'task-failed' : on_task_failed
                    # })
                    recv.capture(limit=None, timeout=None, wakeup=True)

            except (KeyboardInterrupt, SystemExit):
                raise

            except Exception:
                # unable to capture
                pass

            time.sleep(self.interval)

if __name__ == '__main__':
    # app = Celery(broker='redis://localhost:6379/0')
    m = MonitorThread(app)



        #           'task-revoked' : on_event,

        # [('local_received', 1455784782.930694), (u'uuid', u'my-bad-ass2'), (u'clock', 1050), (u'timestamp', 1455784781.92567), (u'hostname', u'celery@larss-MacBook-Pro.local'), (u'pid', 1780), (u'utcoffset', 0), (u'type', u'task-started')]
