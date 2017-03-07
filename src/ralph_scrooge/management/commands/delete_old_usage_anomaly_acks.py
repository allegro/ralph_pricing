# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import UsageAnomalyAck

logger = logging.getLogger(__name__)


def valid_num_months(num):
    try:
        num_ = int(num)
        if num_ <= 0:
            raise Exception()
    except Exception:
        raise argparse.ArgumentTypeError(
            "Invalid number of months: {}.".format(num)
        )
    return num_


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-m',
            type=valid_num_months,
            dest='num_months',
            default=2,
            help=_(
                "Acknowledgements older than `today - NUM_MONTHS` will be "
                "deleted."
            )
        )

    def handle(self, num_months, *args, **options):
        min_date = datetime.date.today() - relativedelta(months=num_months)
        logger.info(
            'Deleting UsageType anomaly acknowledgements older than '
            '{:%Y-%m-%d}...'.format(min_date)
        )
        qs = UsageAnomalyAck.objects.filter(anomaly_date__lt=min_date)
        qs_count = qs.count()
        if qs.exists():
            qs.delete()
        logger.info(
            'Number of UsageType anomaly acknowledgements deleted: {}.'
            .format(qs_count)
        )
