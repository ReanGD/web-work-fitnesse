# -*- coding: utf-8 -*-
import os
import re
import sys
import fnmatch
import jenkinsapi
import lxml.objectify

from django.db import transaction
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist

from fitnesse.models import Job, Build, KeyBuildArtifact, BuildArtifact, Suite, Test, KeyTestArtifact, TestArtifact
import fitnesse.helper.settings as settings


class Jenkins:

    def __init__(self, jenkins_url, job_name):
        self.instance = jenkinsapi.jenkins.Jenkins(jenkins_url)
        self.job = self.instance[job_name]

    def get_builds_id(self):
        last_complited = self.job.get_last_completed_buildnumber()
        return [build_id for build_id in sorted(self.job.get_build_dict().keys()) if build_id <= last_complited]

    def get_suite_artifacts(self, build_id):
        build = self.job[build_id]
        artifacts = build.get_artifact_dict()
        for name in fnmatch.filter(artifacts.keys(), "SuiteCheck*.xml"):
            yield artifacts[name].get_data()

    def get_log_fitnesse_artifacts(self, build_id):
        build = self.job[build_id]
        artifacts = dict((af.url, af) for af in build.get_artifacts())

        for url in fnmatch.filter(artifacts.keys(), "*hvClientW8/Fitnesse/log.txt"):
            yield artifacts[url].get_data()

    def get_start_time(self, build_id):
        build = self.job[build_id]
        return build.get_timestamp()

class Db:

    @transaction.atomic
    def get_job(self, job_name):
        try:
            rec = Job.objects.get(name = job_name)
        except ObjectDoesNotExist:
            rec = Job(name = job_name)
            rec.save()
            settings.set_max_buids(rec, 50)

        return rec

    @transaction.atomic
    def get_build(self, job, build_number):
        try:
            rec = Build.objects.get(number = build_number, job_ptr = job)
            if not rec.is_load:
                Suite.objects.filter(build_ptr = rec).delete()
                BuildArtifact.objects.filter(build_ptr = rec).delete()
        except ObjectDoesNotExist:
            rec = Build(job_ptr = job, number = build_number, is_load = False, error_description = None, is_success = True)
            rec.save()
        
        return rec

    @transaction.atomic
    def get_suite(self, build, suite_name, run_durations):
        rec = Suite(build_ptr = build, name = escape(suite_name), run_durations = run_durations, is_load = True, error_description = None, is_success = True)
        rec.save()

        return rec

    @transaction.atomic
    def add_test(self, suite, test_number, test_name, run_durations, is_success, html_content):
        rec = Test(suite_ptr = suite, number = test_number, name = escape(test_name), run_durations = run_durations, is_success = is_success)
        rec.save()
        key_rec = KeyTestArtifact.objects.get(key = "fitnesse_result")
        TestArtifact(test_ptr = rec, key_ptr = key_rec, content = html_content).save()

    @transaction.atomic
    def add_artifact(self, build, key, subkey, content):
        key_rec = KeyBuildArtifact.objects.get(key = key, subkey = subkey)
        rec = BuildArtifact(build_ptr = build, key_ptr = key_rec, content = content)
        rec.save()

def _parse_suite_artifact(db, build, text):
    root = lxml.objectify.fromstring(text)
    suite = db.get_suite(build, root.rootPath.text.split(".")[-1], int(root.totalRunTimeInMillis.text))

    try:
        result = root.result
    except AttributeError, e:
        suite.save()
        return suite.is_success

    try:
        tests = {}
        for test_number, test_node in enumerate(result):
            is_success = (int(test_node.counts.wrong.text) == 0) and (int(test_node.counts.exceptions.text) == 0)
            if not is_success:
                suite.is_success = False
            test_name = test_node.relativePageName.text
            if test_name in tests:
                tests[test_name] += 1
                test_name += str(tests[test_name])
            else:
                tests[test_name] = 1
            db.add_test(suite, test_number, test_name, int(test_node.runTimeInMillis.text), is_success, test_node.content.text.encode('utf-8'))


        suite.save()
        return suite.is_success
    except Exception, e:
        print("load error: %s" % str(e))
        suite.is_load = False
        suite.error_description = str(e)
        suite.save()
        raise Exception("Suite %s load with error: %s" % (suite.name, str(e)))

def _build_enumerator(db, jenkins, job):
    for build_number in jenkins.get_builds_id():
        build = db.get_build(job, build_number)
        if not build.is_load:
            print(build_number)
            yield build

def import_job(job_name):
    db = Db()
    job = db.get_job(job_name)
    jenkins = Jenkins(settings.get_jenkins_url(), job_name)

    for build in _build_enumerator(db, jenkins, job):
        try:
            for artifact_text in jenkins.get_suite_artifacts(build.number):
                if len(artifact_text) != 0:
                    is_success = _parse_suite_artifact(db, build, artifact_text)
                    if not is_success:
                        build.is_success = False

            for artifact_text in jenkins.get_log_fitnesse_artifacts(build.number):
                if len(artifact_text) != 0:
                    db.add_artifact(build, "ClientW8", "fitnesse_log", artifact_text)

            build.start_time = jenkins.get_start_time(build.number)
            build.is_load = True
        except Exception, e:
            print("load error: %s" % str(e))
            build.is_load = False
            build.error_description = str(e)
        build.save()
    
    Build.objects.filter(pk__in = Build.objects.filter(job_ptr = job).order_by('-number').values_list('pk')[settings.get_max_buids(job):]).delete()

if __name__ == "__main__":
    pass
