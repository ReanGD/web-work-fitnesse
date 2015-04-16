from django.contrib import admin
from fitnesse.models import CommonSettings, Job, JobSettings, Build, KeyBuildArtifact, BuildArtifact, Suite, Test, KeyTestArtifact, TestArtifact

admin.site.register(CommonSettings)
admin.site.register(Job)
admin.site.register(JobSettings)
admin.site.register(Build)
admin.site.register(KeyBuildArtifact)
admin.site.register(BuildArtifact)
admin.site.register(Suite)
admin.site.register(Test)
admin.site.register(KeyTestArtifact)
admin.site.register(TestArtifact)
