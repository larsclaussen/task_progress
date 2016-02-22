from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.http import JsonResponse
from django.views.generic import TemplateView

from task_progress.celery import app
from tasks import do_work, add
from celery.result import AsyncResult
import json
from django.shortcuts import render_to_response
import uuid

from monitor import MonitorThread


def index(request):
    return HttpResponse("Hello, world. Monitor.")



# class JSONResponseMixin(object):
#     def render_to_response(self, context):
#         "Returns a JSON response containing 'context' as payload"
#         return self.get_json_response(self.convert_context_to_json(context))
#
#     def get_json_response(self, content, **httpresponse_kwargs):
#         "Construct an `HttpResponse` object."
#         return http.HttpResponse(content,
#                                  content_type='application/json',
#                                  **httpresponse_kwargs)
#
#     def convert_context_to_json(self, context):
#         "Convert the context dictionary into a JSON object"
#         # Note: This is *EXTREMELY* naive; in reality, you'll need
#         # to do much more complex handling to ensure that arbitrary
#         # objects -- such as Django model instances or querysets
#         # -- can be serialized as JSON.
#         return json.dumps(context)

class MonitorThreadMixin(object):
    monitor = MonitorThread(app)
    names = monitor.list_registered_jobs()
    print "names ", names


class MonitorView(MonitorThreadMixin, TemplateView):
    template_name = "monitor.html"

    def get(self, request, *args, **kwargs):
        print "jobs done ", self.monitor.jobs_done
        if self.request.is_ajax():


            print 'AJAX!\n'
            quest = request.GET.get('q') or None
            print 'quest! ', quest
            if quest == 'done':
                return render_to_response(
                    'done.html', {'jobs_done': self.monitor.jobs_done}
                )
            # start a new job
            elif quest == 'start':
                job = do_work.apply_async(task_id='my-bad-ass-{}'.format(uuid.uuid4().hex))
                print 'job.state ', job.state
                data = job.result or job.state
                return JsonResponse(data, safe=False)


            # no get parameters, return the running jobs list
            else:
                return render_to_response(
                    'active.html', {'running_jobs': self.monitor.list_running_jobs}
                )
        else:
            context = self.get_context_data()
            return render_to_response("monitor.html", context=context)

    def get_context_data(self, **kwargs):
        context = super(MonitorView, self).get_context_data(**kwargs)
        return context

class JobNamesView(MonitorThreadMixin, TemplateView):
    template_name = "names.html"


class ProgressView(MonitorThreadMixin, TemplateView):
    template_name = "progress.html"

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            quest = request.GET.get('q') or None
            print 'quest! ', quest
            # start a new job
            if quest == 'progress':
                data = {}
                res = do_work.apply_async(task_id='my-bad-ass-{}'.format(uuid.uuid4().hex))
                job_id = {"id": res.id}
                return JsonResponse(job_id, safe=False)

            elif quest == 'poll_state':
                job_id = self.request.GET['job_id']
                print 'job_id ', job_id

                job = AsyncResult(job_id)
                data = job.result or job.state
                print "data ", data
                return JsonResponse(data, safe=False)
        else:
            context = self.get_context_data()
            return render_to_response("progress.html", context=context)

    def get_context_data(self, **kwargs):
        context = super(ProgressView, self).get_context_data(**kwargs)
        return context


def poll_state(request):
    """ A view to report the progress to the user """
    if 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')

    print 'job_id ', job_id

    job = AsyncResult(job_id)
    data = job.result or job.state
    return JsonResponse(data, safe=False)


def init_work(request):
    """ A view to start a background job and redirect to the status page """
    #job = do_work.delay()
    job = do_work.apply_async(task_id='my-bad-ass')
    print 'job.state ', job.state
    job.id
    add_result = add.delay(2,2)
    print 'add.state ', add_result.state

    return HttpResponseRedirect(reverse('poll_state') + '?job=' + job.id)


def start_job():
    """ A view to start a background job and redirect to the status page """
    #job = do_work.delay()
    job = do_work.apply_async(task_id='my-bad-ass')
    print 'job.state ', job.state


# <script type="text/javascript">
#   jQuery(document).ready(function() {
#
#    // pole state of the current task
#    var PollState = function(task_id) {
#     jQuery.ajax({
#      url: "poll_state",
#      type: "GET",
#      data: "task_id=" + task_id,
#     }).done(function(task){
#      console.log(task);
#      if (task.process_percent) {
#       jQuery('.bar').css({'width': task.process_percent + '%'});
#       jQuery('.bar').html(task.process_percent + '%')
#      } else {
#       jQuery('.status').html(task);
#      };
#
#      // create the infinite loop of Ajax calls to check the state
#      // of the current task
#      PollState(task_id);
#     });
#    }
#
#    PollState('{{ task_id }}');
#   });
#  </script>
#
#
# (function worker() {
#   $.ajax({
#     url: 'poll_state',
#     type: 'get'
#     success: function(data) {
#       $('.result').html(data);
#     },
#     complete: function() {
#       // Schedule the next request when the current one's complete
#       setTimeout(worker, 5000);
#     }
#   });
# })();
#
#
# #progressBar {
#     width: 400px;
#     height: 22px;
#     border: 1px solid #111;
#     background-color: #292929;
# }
#
# #progressBar div {
#     height: 100%;
#     color: #fff;
#     text-align: right;
#     line-height: 22px; /* same as #progressBar height if we want text middle aligned */
#     width: 0;
#     background-color: #0099ff;
# }
#
# function progress(percent, $element) {
#     var progressBarWidth = percent * $element.width() / 100;
#     $element.find('div').animate({ width: progressBarWidth }, 500).html(percent + "% ");
# }
#
# progress(80, $('#progressBar'));

# In [10]: from celery.task.control import inspect
#
# In [11]: i = inspect()
#
# In [12]: i.registered()
# Out[12]:
# {u'celery@larss-MacBook-Pro.local': [u'task_progress.celery.debug_task',
#   u'tasks.add',
#   u'tasks.do_work',
#   u'tasks.mul',
#   u'tasks.xsum']}
#
# In [13]: i.active()