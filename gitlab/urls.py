from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from gitlab import views

urlpatterns = patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/app/favicon.ico')),
    url(r'^push_event/hv$', views.push_event_hv),
    url(r'^push_event/web$', views.push_event_web),
    url(r'^push_event/monitoring$', views.push_event_monitoring),
)
