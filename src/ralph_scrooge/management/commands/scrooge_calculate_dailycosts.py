# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import date, datetime, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.management.commands._scrooge_base import ScroogeBaseCommand
from ralph_scrooge.plugins.cost.collector import Collector

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Generate report with tenants instances and cost of particular flavors
    (if tenants are billed based on ceilometer) or simple usages.
    """
    option_list = ScroogeBaseCommand.option_list + (
        make_option(
            '-s', '--start',
            dest='start',
            default=None,
            help=_('Date from which generate report for'),
        ),
        make_option(
            '--end',
            dest='end',
            default=None,
            help=_('Date to which generate report for'),
        ),
        make_option(
            '--forecast',
            dest='forecast',
            default=False,
            action='store_true',
            help=_('Set to use forecast prices and costs'),
        ),
        make_option(
            '-p',
            dest='plugins',
            action='append',
            type='str',
            default=[],
            help=_('Plugins to calculate missing costs'),
        ),
        make_option(
            '-t',
            dest='type',
            type='choice',
            choices=['simple_usage', 'ceilometer', 'nova', 'volume'],
            default='ceilometer',
            help=_('Type of OpenStack usage'),
        ),
    )

    def _calculate_missing_dates(self, start, end, forecast, plugins):
        """
        Calculate costs for dates on which costs were not previously calculated
        """
        collector = Collector()
        dates_to_calculate = collector._get_dates(start, end, forecast, False)
        plugins = [pl for pl in collector.get_plugins() if pl.name in plugins]
        for day in dates_to_calculate:
            costs = collector.process(day, forecast, plugins=plugins)
            processed = collector._create_daily_costs(day, costs, forecast)
            collector.save_period_costs(day, day, forecast, processed)

    def _parse_date(self, date_):
        """
        Parse given date or returns default (yesterday).
        """
        if date_:
            return datetime.strptime(date_, '%Y-%m-%d').date()
        else:
            return date.today() - timedelta(days=1)

    def handle(self, *args, **options):
        start = self._parse_date(options['start'])
        end = self._parse_date(options['end'])
        self._calculate_missing_dates(
            start, end, options['forecast'], options['plugins']
        )
