from django.db import models


class CommonSettings(models.Model):
    name = models.CharField(max_length=500, unique=True)
    number = models.IntegerField(null=True, default=None)
    text = models.CharField(max_length=500, null=True, default=None)

    def __unicode__(self):
        return "%s" % self.name


class Job(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __unicode__(self):
        return "%s" % self.name


class JobSettings(models.Model):
    job_ptr = models.ForeignKey(Job)
    name = models.CharField(max_length=500)
    number = models.IntegerField(null=True, default=None)
    text = models.CharField(max_length=500, null=True, default=None)

    class Meta:
        unique_together = (("job_ptr", "name"),)

    def __unicode__(self):
        return "%s: %s" % (self.job_ptr.name, self.name)


class Build(models.Model):
    job_ptr = models.ForeignKey(Job)
    number = models.IntegerField(default=-1)
    is_load = models.BooleanField(default=False)
    error_description = models.TextField(null=True, default=None)
    is_success = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, default=None)

    class Meta:
        unique_together = (("job_ptr", "number"),)

    def __unicode__(self):
        if self.is_load:
            return "%s (%i)" % (self.job_ptr.name, self.number)
        else:
            return "%s (%i): error: %s" % (self.job_ptr.name, self.number, self.error_description)


class KeyBuildArtifact(models.Model):
    key = models.CharField(null=False, max_length=100)
    subkey = models.CharField(null=False, max_length=100)

    class Meta:
        unique_together = (("key", "subkey"),)

    def __unicode__(self):
        return "%s.%s" % (self.key, self.subkey)


class BuildArtifact(models.Model):
    build_ptr = models.ForeignKey(Build)
    key_ptr = models.ForeignKey(KeyBuildArtifact)
    content = models.BinaryField(default=None)

    class Meta:
        unique_together = (("build_ptr", "key_ptr"),)

    def __unicode__(self):
        job_name = self.build_ptr.job_ptr.name
        build_number = self.build_ptr.number
        return "%s (%i): %s" % (job_name, build_number, unicode(self.key_ptr))


class Suite(models.Model):
    build_ptr = models.ForeignKey(Build)
    name = models.CharField(max_length=500)
    run_durations = models.IntegerField(default=0)
    is_load = models.BooleanField(default=False)
    error_description = models.TextField(null=True, default=None)
    is_success = models.BooleanField(default=False)

    class Meta:
        unique_together = (("build_ptr", "name"),)

    def __unicode__(self):
        job_name = self.build_ptr.job_ptr.name
        build_number = self.build_ptr.number
        if self.is_load:
            return "%s (%i): %s" % (job_name, build_number, self.name)
        else:
            return "%s (%i): %s: error: %s" % (job_name, build_number, self.name, self.error_description)


class Test(models.Model):
    suite_ptr = models.ForeignKey(Suite)
    number = models.IntegerField(default=0)
    name = models.CharField(max_length=500)
    run_durations = models.IntegerField(default=0)
    is_success = models.BooleanField(default=False)

    class Meta:
        unique_together = (("suite_ptr", "name"),)

    def __unicode__(self):
        job_name = self.suite_ptr.build_ptr.job_ptr.name
        build_number = self.suite_ptr.build_ptr.number
        return "%s (%i): %i. %s.%s" % (job_name, build_number, self.number, self.suite_ptr.name, self.name)


class KeyTestArtifact(models.Model):
    key = models.CharField(null=False, max_length=100, unique=True)

    def __unicode__(self):
        return self.key


class TestArtifact(models.Model):
    test_ptr = models.ForeignKey(Test)
    key_ptr = models.ForeignKey(KeyTestArtifact)
    content = models.BinaryField(default=None)

    class Meta:
        unique_together = (("test_ptr", "key_ptr"),)

    def __unicode__(self):
        return "%s.%s: %s" % (self.test_ptr.suite_ptr.name, self.test_ptr.name, self.key_ptr.key)
