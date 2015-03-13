#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ralph_scrooge.utils.tasks import create_dailycosts_partitions


class Command(BaseCommand):
    help = 'Create required DB partitions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating missing partitions...\n')
        create_dailycosts_partitions()
        self.stdout.write('Done\n')
