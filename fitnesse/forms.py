# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from fitnesse.models import Job

import fitnesse.helper.settings as settings


def common_settings_show(request):
    return render(request, 'fitnesse/common_settings.html', {'JenkinsUrl': settings.get_jenkins_url()})

def common_settings_save(request):
    settings.set_jenkins_url(request.POST['JenkinsUrl'])
    return HttpResponseRedirect(reverse('fitnesse:jobs'))

def job_settings_show(request, job_id):
    job = get_object_or_404(Job, pk = job_id)
    return render(request, 'fitnesse/job_settings.html', {'Job': job, 'MaxBuilds': settings.get_max_buids(job)})

def job_settings_save(request, job_id):
    job = get_object_or_404(Job, pk = job_id)
    settings.set_max_buids(job, request.POST['MaxBuilds'])
    return HttpResponseRedirect(reverse('fitnesse:jobs'))
