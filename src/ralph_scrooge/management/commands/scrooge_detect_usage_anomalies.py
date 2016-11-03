# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import math
import textwrap
from datetime import datetime, date, timedelta

from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand

from ralph_scrooge.models import UsageType, DailyUsage


log = logging.getLogger(__name__)


# XXX choice?
ANOMALY_CATEGORIES = {

}

# XXX can be overridden on per-UsageType basis
SENSITIVITY = 0.2

MSG_TEMPLATE = ""

NOTIFY_THRESHOLDS = [timedelta(days=d) for d in (1, 7, 14)]

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            default=False,
            help="Don't send any notifications"
        )

    def _detect_anomalies(self):
        results = OrderedDict()
        for usage in UsageType.objects.order_by('name'):
            results[usage.name] = self.get_standard_usages_count(date, usage)

    def _group_by_type(self):
        pass

    def _send_notifications(self):
        pass

    def handle(self, dry_run, *args, **options):
        anomalies = self._detect_anomalies()
        anomalies_ = self._group_by_type(anomalies)
        if not dry_run:
            self._send_notifications(anomalies_)
