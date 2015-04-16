from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from gitlab import views

urlpatterns = patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/app/favicon.ico')),
    url(r'^push_event/.*$', views.push_event, name='push_event')
)
