from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^fitnesse/', include('fitnesse.urls', namespace="fitnesse")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^gitlab/', include('gitlab.urls', namespace="gitlab")),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/app/favicon.ico')),
)
