from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.http import JsonResponse

from tasks import do_work, add
from celery.result import AsyncResult

def index(request):
    return HttpResponse("Hello, world. Monitor.")

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
    job = do_work.delay()
    print 'job.state ', job.state
    add_result = add.delay(2,2)
    print 'add.state ', add_result.state

    return HttpResponseRedirect(reverse('poll_state') + '?job=' + job.id)


<script type="text/javascript">
  jQuery(document).ready(function() {

   // pole state of the current task
   var PollState = function(task_id) {
    jQuery.ajax({
     url: "poll_state",
     type: "GET",
     data: "task_id=" + task_id,
    }).done(function(task){
     console.log(task);
     if (task.process_percent) {
      jQuery('.bar').css({'width': task.process_percent + '%'});
      jQuery('.bar').html(task.process_percent + '%')
     } else {
      jQuery('.status').html(task);
     };

     // create the infinite loop of Ajax calls to check the state
     // of the current task
     PollState(task_id);
    });
   }

   PollState('{{ task_id }}');
  });
 </script>


(function worker() {
  $.ajax({
    url: 'poll_state',
    type: 'get'
    success: function(data) {
      $('.result').html(data);
    },
    complete: function() {
      // Schedule the next request when the current one's complete
      setTimeout(worker, 5000);
    }
  });
})();


#progressBar {
    width: 400px;
    height: 22px;
    border: 1px solid #111;
    background-color: #292929;
}

#progressBar div {
    height: 100%;
    color: #fff;
    text-align: right;
    line-height: 22px; /* same as #progressBar height if we want text middle aligned */
    width: 0;
    background-color: #0099ff;
}

function progress(percent, $element) {
    var progressBarWidth = percent * $element.width() / 100;
    $element.find('div').animate({ width: progressBarWidth }, 500).html(percent + "% ");
}

progress(80, $('#progressBar'));