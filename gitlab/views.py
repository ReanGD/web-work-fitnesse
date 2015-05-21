# -*- coding: utf-8 -*-

from django.db.models import Count, Sum, Max
from django.utils.html import escape
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404

import json
import logging
import jenkinsapi

import fitnesse.helper.settings as settings

logger = logging.getLogger(__name__)

def push_event(request):
    logger.debug("=> [push_event]")
    logger.debug("    run GitMirror")
    jenk = jenkinsapi.jenkins.Jenkins(settings.get_jenkins_url())
    git_mirror_job = jenk.get_job("GitMirror")
    git_mirror_job.invoke('QZ43NKLOYITZ5Y477D86XK37VTH5XIUF')

    hook_info = json.loads(str(request.body))
    logger.debug(" ref = " + hook_info['ref'])
    logger.debug(" user_name = " + hook_info['user_name'])

    if hook_info['ref'] == "refs/heads/master" and hook_info['user_name'] != "Jenkins":
        logger.debug("    process master branch")

        # logger.debug("    run Packages-Pipeline")
        # packages_pl_job = jenk.get_job("Packages-Pipeline")
        # packages_pl_job.invoke('3MDZ0B66R79Y9MUKA66R2JFYO7GJXQKG')

        logger.debug("    run hvGate-Pipeline-Run")
        hvGate_pl_job = jenk.get_job("hvGate-Pipeline-Run")
        hvGate_pl_job.invoke('G08CKH1LE5L6R13LP0AGSLNO7DDXC2VN')

    logger.debug("<= [push_event]")
    return HttpResponse("<html><head></head><body>OK</body></html>")

