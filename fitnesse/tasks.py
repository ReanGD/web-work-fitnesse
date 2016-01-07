# -*- coding: utf-8 -*-

import logging
from celery import shared_task
from django.http import HttpResponse
import fitnesse.import_data

logger = logging.getLogger(__name__)


@shared_task
def import_job_task(job_name):
    try:
        logger.debug("Start import " + job_name)
        fitnesse.import_data.import_job(job_name)
        logger.debug("Finish import " + job_name)
    except Exception:
        logger.error("Error import " + job_name)


def import_job(request, job_name):
    import_job_task.apply_async(args=[job_name])
    return HttpResponse("Ok")
