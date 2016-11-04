# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import calendar
import logging
import math
import textwrap
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand

from ralph_scrooge.models import UsageType, DailyUsage
from ralph_scrooge.rest.service_environment_costs import date_range  # XXX


log = logging.getLogger(__name__)


# XXX choice?
ANOMALY_CATEGORIES = {

}

# XXX can be overridden on per-UsageType basis
SENSITIVITY = 0.2

MSG_TEMPLATE = ""

NOTIFY_THRESHOLDS = [timedelta(days=d) for d in (1, 7, 14)]


def get_negative_month_range(end_date=None):
    if end_date is None:
        end_date = date.today() - timedelta(days=1)
    start_date = end_date - relativedelta(months=1)
    return date_range(start_date, end_date)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            default=False,
            help="Don't send any notifications"
        )


    def get_standard_usages_count(self, date, usage):
        return DailyUsage.objects.filter(date=date, type=usage).count()


    def _detect_anomalies(self):

        results = OrderedDict()
        for date_ in get_negative_month_range():
            for usage in UsageType.objects.order_by('name'):
                results[usage.name] = self.get_standard_usages_count(
                    date_, usage
                )
        # XXX resume from here

    def _group_by_type(self):
        pass

    def _send_notifications(self):
        pass

    def handle(self, dry_run, *args, **options):
        anomalies = self._detect_anomalies()
        anomalies_ = self._group_by_type(anomalies)
        if not dry_run:
            self._send_notifications(anomalies_)
