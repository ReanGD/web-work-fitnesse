# -*- coding: utf-8 -*-

from fitnesse.models import CommonSettings, JobSettings
from django.core.exceptions import ObjectDoesNotExist


def get_jenkins_url():
    try:
        return CommonSettings.objects.get(name = "JenkinsUrl").text
    except Exception, e:
        return 'http://172.28.1.33/'

def set_jenkins_url(value):
    try:
        rec = CommonSettings.objects.get(name="JenkinsUrl")
        rec.text = value
    except ObjectDoesNotExist:
        rec = CommonSettings(name = "JenkinsUrl", text = value)
    rec.save()

def get_max_buids(job_ptr):
    try:
        return JobSettings.objects.get(job_ptr = job_ptr, name = "MaxBuilds").number
    except Exception, e:
        return 50

def set_max_buids(job_ptr, value):
    try:
        rec = JobSettings.objects.get(job_ptr = job_ptr, name="MaxBuilds")
        rec.number = value
    except ObjectDoesNotExist:
        rec = JobSettings(job_ptr = job_ptr, name = "MaxBuilds", number = value)
    rec.save()


if __name__ == "__main__":
    pass
