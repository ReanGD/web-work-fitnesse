# -*- coding: utf-8 -*-

from django.http import HttpResponse

import json
import logging
import jenkinsapi

import fitnesse.helper.settings as settings

logger = logging.getLogger(__name__)


def push_event_hv(request):
    logger.debug("=> [push_event_hv]")
    logger.debug("    run GitMirror")
    jenk = jenkinsapi.jenkins.Jenkins(settings.get_jenkins_url())
    git_mirror_job = jenk.get_job("GitMirror")
    git_mirror_job.invoke('QZ43NKLOYITZ5Y477D86XK37VTH5XIUF')

    hook_info = json.loads(request.body.decode())
    logger.debug(" ref = " + hook_info['ref'])
    logger.debug(" user_name = " + hook_info['user_name'])

    if hook_info['ref'] == "refs/heads/master" and hook_info['user_name'] != "Jenkins":
        logger.debug("    hv: process master branch")

        # logger.debug("    run Packages-Pipeline")
        # packages_pl_job = jenk.get_job("Packages-Pipeline")
        # packages_pl_job.invoke('3MDZ0B66R79Y9MUKA66R2JFYO7GJXQKG')

        logger.debug("    run hvGate-Pipeline-Run")
        hvGate_pl_job = jenk.get_job("hvGate-Pipeline-Run")
        hvGate_pl_job.invoke('G08CKH1LE5L6R13LP0AGSLNO7DDXC2VN')

    logger.debug("<= [push_event_hv]")
    return HttpResponse("<html><head></head><body>OK</body></html>")


def push_event_web(request):
    logger.debug("=> [push_event_web]")

    jenkins = jenkinsapi.jenkins.Jenkins(settings.get_jenkins_url())
    hook_info = json.loads(request.body.decode())
    logger.debug(" ref = " + hook_info['ref'])
    logger.debug(" user_name = " + hook_info['user_name'])

    if hook_info['ref'] == "refs/heads/master" and hook_info['user_name'] != "Jenkins":
        logger.debug("    web: process master branch")
        logger.debug("    run hvGate-Pipeline-Run")
        job = jenkins.get_job("Web-Pipeline-Run")
        job.invoke('F17CKH1LE5L6R13LP0AGSLNO7DDXC3ER')

    logger.debug("<= [push_event_web]")
    return HttpResponse("<html><head></head><body>OK</body></html>")
