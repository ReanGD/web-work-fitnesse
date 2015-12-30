# -*- coding: utf-8 -*-

from django.db.models import Sum, Max, Q
from aggregate_if import Count
from django.utils.html import escape
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404

from fitnesse.models import Job, Build, KeyBuildArtifact, BuildArtifact, Suite, Test, KeyTestArtifact, TestArtifact
import fitnesse.helper.settings as settings
import fitnesse.helper.tasks as tasks
import fitnesse.import_data

import re
import json
import time
import pytz
import collections

def changelog(request):
    return render(request, 'fitnesse/changelog.html')

def jobs(request):
    jobs = Job.objects.all().annotate(build_count=Count('build'), build_last=Max('build__number'), start_time=Max('build__number'), _stat=Max('build__number')).order_by('name')
    last_jobs = [job.build_last for job in jobs]        
    builds_results = Test.objects.filter(suite_ptr__build_ptr__number__in = last_jobs).values('suite_ptr__build_ptr__job_ptr__id', 'suite_ptr__build_ptr__start_time').annotate(dummy=Count('suite_ptr__build_ptr__id'), total = Count('id'), count_succeess = Count('is_success', only=Q(is_success=True))).order_by('suite_ptr__build_ptr__number')    
    local_tz = pytz.timezone('Europe/Moscow')
    result_map = {it['suite_ptr__build_ptr__job_ptr__id']:
                      {'last_build_stat': '%i of %i failed' % (it['total'] - it['count_succeess'], it['total']),
                       'start_time': local_tz.normalize(it['suite_ptr__build_ptr__start_time'].astimezone(local_tz)).strftime('%H:%M %d/%m/%y') if it['suite_ptr__build_ptr__start_time'] is not None else None}
                            for it in builds_results}

    for job in jobs:
        job.last_build_stat = result_map[job.id]['last_build_stat'] if job.id in result_map else '-'
        job.build_last = '-' if job.build_last is None else '#' + str(job.build_last)
        job.start_time = result_map[job.id]['start_time'] if job.id in result_map and result_map[job.id]['start_time'] is not None else '-'

    return render(request, 'fitnesse/jobs.html', {'jobs': jobs})

def job_charts(request, job_id):
    job = get_object_or_404(Job, pk = job_id)
    query = Test.objects.filter(suite_ptr__build_ptr__job_ptr = job).values('suite_ptr__build_ptr__number').annotate(dummy=Count('suite_ptr__build_ptr__id'), total = Count('id'), count_succeess = Count('is_success', only=Q(is_success=True))).order_by('suite_ptr__build_ptr__number')
    
    separators = (',', ':')
    builds = json.dumps(['#' + str(it['suite_ptr__build_ptr__number']) for it in query], separators=separators)
    succeess = json.dumps([it['count_succeess'] for it in query], separators=separators)
    error = json.dumps([it['total'] - it['count_succeess'] for it in query], separators=separators)

    return render(request, 'fitnesse/job_charts.html', {'Job': job, 'Builds': builds, 'Succeess': succeess, 'Error': error})

def _get_tests_by_job(job):
    all_tests = Test.objects.filter(suite_ptr__build_ptr__job_ptr = job).values('id', 'name', 'is_success', 'suite_ptr__name', 'suite_ptr__build_ptr__number').order_by('suite_ptr__name', 'number', '-suite_ptr__build_ptr__number')
    for it in all_tests:
        yield it['id'], it['is_success'], it['name'], it['suite_ptr__name'], it['suite_ptr__build_ptr__number']
    yield None, None, None, None, None

def results_aggregation(request, job_id):
    t_begin = time.time()

    separators = (',', ':')
    job = get_object_or_404(Job, pk = job_id)

    builds = Build.objects.filter(job_ptr = job).order_by('-number')
    if not builds:
        return render(request, 'fitnesse/not_load.html', {'job': job})
    build_count = builds.count()
    build_map = {build.number: num for (num, build) in enumerate(builds)}
    build_list = json.dumps([it.number for it in builds], separators=separators)

    tests = {}
    generator = iter(_get_tests_by_job(job))
    test_id, test_success, old_test_name, old_suite_name, build_number = next(generator)
    test_result = [[0, 0]]*build_count
    test_result[build_map[build_number]] = [test_id, 1 if test_success else 0]
    suite_result = collections.OrderedDict()
    
    for test_id, test_success, test_name, suite_name, build_number in generator:
        if test_name != old_test_name:
            suite_result[old_test_name] = test_result
            old_test_name = test_name
            if suite_name == old_suite_name and test_name in suite_result.keys():
                test_result = suite_result[test_name]
            else:
                test_result = [[0, 0]]*build_count

        if suite_name != old_suite_name:
            tests[old_suite_name] = suite_result
            old_suite_name = suite_name
            suite_result = collections.OrderedDict()

        if test_id is not None:
            test_result[build_map[build_number]] = [test_id, 1 if test_success else 0]    

    url_base = '"' + settings.get_jenkins_url() + '/job/' + job.name + '/"'
    r =  render(request, 'fitnesse/results_aggregation.html', {'job': job, 'builds': build_list, 'build_count': build_count,'tests': json.dumps(tests, separators=separators), 'url_base': url_base})
    return r

def find_suite_log(artifact, suite_name, test_name):
    start_pattern = '!!! (\d|\.|\:|\ )+start test: \".*\.%s.%s\" !!!' % (suite_name, test_name)
    stop_pattern = '!!! (\d|\.|\:|\ )+stop test: \".*\.%s.%s\" !!!.*\s' % (suite_name, test_name)

    text = str(artifact.content)
    m_start = re.search(start_pattern, text)
    m_stop = re.search(stop_pattern, text)
    if (not m_start) or (not m_stop):
        return {'before': '', 'test': 'not found', 'after': ''}

    before_text = '\r'.join(text[:m_start.start()].split('\r')[-20:])
    find_text = text[m_start.start():m_stop.end()].rstrip()
    after_text = '\r'.join(text[m_stop.end():].split('\r')[:20])

    def show_error(text, error_str):
        return text.replace(error_str, '<div class="fitnesse-error">' + error_str + '</div>')        

    result = []
    for it in [before_text, find_text, after_text]:
        it = escape(unicode(it, '866')).replace('\r\n', '<br/>').replace('\r', '<br/>').replace('\n', '<br/>')
        it = show_error(show_error(show_error(it, 'RPC_E_CALL_CANCELED'), 'System.Management.IWbemServices'), u'Узел назначения недоступен')
        result.append(it)

    return {'before': result[0], 'test': result[1], 'after': result[2]}

def test_result(request, job_id, test_id):
    job = get_object_or_404(Job, pk = job_id)
    test_info = Test.objects.filter(pk = test_id).values('name', 'suite_ptr__name', 'suite_ptr__build_ptr', 'suite_ptr__build_ptr__number')
    if not test_info:
        raise Http404

    build_id = test_info[0]['suite_ptr__build_ptr']
    build_number = str(test_info[0]['suite_ptr__build_ptr__number'])
    suite_name = str(test_info[0]['suite_ptr__name'])
    test_name = str(test_info[0]['name'])

    artifact_key = get_object_or_404(KeyBuildArtifact, key = "ClientW8", subkey = "fitnesse_log")
    artifact = get_object_or_404(BuildArtifact, build_ptr = build_id, key_ptr = artifact_key)
    fitnesse_result = find_suite_log(artifact, suite_name, test_name)

    test_full_name = '%s.%s' % (suite_name, test_name)
    build_url = settings.get_jenkins_url() + '/job/' + job.name + '/' + build_number
    return render(request, 'fitnesse/test_result.html', {'job': job, 'test_id': test_id, 'build_id': build_number, 'build_url': build_url, 'test_name': test_full_name, 'fitnesse_result': fitnesse_result})

def fitnesse_result(request, job_id, test_id):
    job = get_object_or_404(Job, pk = job_id)
    artifact_key = get_object_or_404(KeyTestArtifact, key = "fitnesse_result")
    artifact = get_object_or_404(TestArtifact, test_ptr = test_id, key_ptr = artifact_key)

    return render(request, 'fitnesse/fitnesse_result.html', {'job': job, 'artifact': artifact})
