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
yesterday = date.today() - timedelta(days=1)


class Command(BaseCommand):
    option_list = ScroogeBaseCommand.option_list + (
        make_option(
            '--date',
            dest='date',
            default=yesterday,
            help=_('Date to which calculate daily costs for'),
        ),
        make_option(
            '--forecast',
            dest='forecast',
            default=False,
            action='store_true',
            help=_('Set to use forecast prices and costs'),  # XXX ?
        ),
        make_option(
            '-p',
            dest='pricing_services',
            action='append',
            type='str',
            default=[],
            help=_('Pricing Services to which calculate daily costs for'),
        ),
    )

    def _calculate_costs(self, date_, forecast, pricing_services):
        collector = Collector()
        plugins = [
            p for p in collector.get_plugins() if p.name in pricing_services
        ]
        processed_costs = collector.process(date_, forecast, plugins=plugins)
        daily_costs = collector._create_daily_costs(
            date_, processed_costs, forecast
        )
        start = end = date_
        collector.save_period_costs(start, end, forecast, daily_costs)

    def _parse_date(self, date_):
        if not isinstance(date_, date):
            return datetime.strptime(date_, '%Y-%m-%d').date()
        else:
            return date_

    def handle(self, *args, **options):
        date_ = self._parse_date(options['date'])
        self._calculate_costs(
            date_, options['forecast'], options['pricing_services']
        )
