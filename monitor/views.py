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
