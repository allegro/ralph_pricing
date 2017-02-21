# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from datetime import datetime

from django.core.management.base import BaseCommand

from ralph_scrooge.utils.cycle_detector import detect_cycles


def valid_date(date_):
    try:
        return datetime.strptime(date_, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid date: '{}'.".format(date_)
        )


class Command(BaseCommand):
    """Calculate daily costs for a given day (defaults to yesterday) and
    pricing service (defaults to all which are bot active and have fixed
    price).
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=valid_date,
            dest='date',
            required=True,
        )

    def handle(self, *args, **options):
        cycles = detect_cycles(options['date'])
        if cycles:
            self.stdout.write('Cycles detected!')
            for cycle in cycles:
                self.stdout.write(' -> '.join(cycle))
        else:
            self.stdout.write('No cycles!')
