# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from ralph_scrooge.sync.publisher import publish_accepted_costs_dump

from ralph_scrooge.utils.common import validate_date as valid_date


class Command(BaseCommand):
    """
    Publish accepted costs to configured subscribers.
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--date-from',
            type=valid_date,
            dest='date_from',
            required=True,
        )
        parser.add_argument(
            '--date-to',
            type=valid_date,
            dest='date_to',
            required=True,
        )
        parser.add_argument(
            '--forecast',
            dest='forecast',
            default=False,
            action='store_true'
        )

    def handle(self, *args, **options):
        publish_accepted_costs_dump(
            options['date_from'], options['date_to'], options['forecast']
        )
        self.stdout.write('Costs published!')
