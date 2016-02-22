from django.conf.urls import patterns, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^init_work$', views.init_work),
    url(r'^poll_state$', views.poll_state, name="poll_state"),
    url(r'^monitor/', views.MonitorView.as_view(), name='monitor'),
    url(r'^names/', views.JobNamesView.as_view(), name='names'),
    url(r'^progress/', views.ProgressView.as_view(), name='progress'),
]
