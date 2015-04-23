from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from fitnesse import views
from fitnesse import forms
from fitnesse import actions

urlpatterns = patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/app/favicon.ico')),
    url(r'^$', views.jobs, name='jobs'),
    url(r'^import_job/(?P<job_name>\S+)/$', actions.import_job, name='import_job'),
    url(r'^changelog/$', views.changelog, name='changelog'),
    url(r'^settings_show/$', forms.common_settings_show, name='common_settings_show'),
    url(r'^settings_save/$', forms.common_settings_save, name='common_settings_save'),
    url(r'^(?P<job_id>\d+)/$', views.results_aggregation, name='results_aggregation'),    
    url(r'^(?P<job_id>\d+)/settings_show/$', forms.job_settings_show, name='job_settings_show'),
    url(r'^(?P<job_id>\d+)/settings_save/$', forms.job_settings_save, name='job_settings_save'),
    url(r'^(?P<job_id>\d+)/charts/$', views.job_charts, name='job_charts'),
    url(r'^(?P<job_id>\d+)/r/(?P<test_id>\d+)/$', views.test_result, name='test_result'),
    url(r'^(?P<job_id>\d+)/r/(?P<test_id>\d+)/fitnesse_result$', views.fitnesse_result, name='fitnesse_result'),
)
