# -*- coding: utf-8 -*-

from celery import shared_task
from django.http import HttpResponse
import fitnesse.import_data


@shared_task
def import_job_task(job_name):
    fitnesse.import_data.import_job(job_name)


def import_job(request, job_name):
    import_job_task.apply_async(args=[job_name])
    return HttpResponse("Ok")
