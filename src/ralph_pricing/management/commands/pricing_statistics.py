# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand

from ralph.util import plugin
from ralph_pricing.app import setup_scrooge_logger
from ralph_pricing.models import DailyStatistics


logger = logging.getLogger(__name__)


class PluginError(Exception):
    pass


class Command(BaseCommand):
    """Retrieve data for pricing for today"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '--first-today',
            dest='first_date',
            default=None,
            help="First date",
        ),
        make_option(
            '--second-today',
            dest='second_date',
            default=None,
            help="First date",
        ),
    )

    def handle(self, first_date, second_date, *args, **options):
        def get_date(date):
            if date:
                date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
            else:
                date= datetime.date.today()
            return date

        get_date(first_date),
        get_date(second_date)
        if first_date == second_date:
            second_date -= datetime.timedelta(days=1)

        DailyStatistics.compare_days(
        )
