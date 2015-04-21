#!/usr/bin/python

import logging
from django.http import HttpResponse
from uwsgidecorators import spool
import fitnesse.import_data

logger = logging.getLogger(__name__)


@spool
def import_job_task(arguments):
    job_name = arguments['job_name']
    try:
        logger.exception("Start import " + job_name)
        fitnesse.import_data.import_job(job_name)
    except Exception:
        logger.exception("Error import " + job_name)


def import_job(request, job_name):
    import_job_task.spool({'job_name': job_name})
    return HttpResponse("Ok")
