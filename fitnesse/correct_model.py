# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

from fitnesse.models import Job, Build, KeyBuildArtifact, BuildArtifact, Suite, Test, KeyTestArtifact, TestArtifact

def main():
    for it in Suite.objects.all():
        it.name = it.name.split(".")[-1]
        it.save()


if __name__ == "__main__":
    main()
