# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from dateutil.relativedelta import relativedelta

from collections import OrderedDict

# from django.conf import settings  # XXX
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.loader import render_to_string

from ralph_scrooge.models import UsageType, DailyUsage
from ralph_scrooge.rest.service_environment_costs import date_range  # XXX


log = logging.getLogger(__name__)

# XXX can be overridden on per-UsageType basis
DIFF_TOLERANCE = 0.2
NOTIFY_THRESHOLDS = [datetime.timedelta(days=d) for d in (1, 7, 14)]


def get_usage_types(names):
    if names:
        ut = UsageType.objects.filter(name__in=names).order_by('name')
    else:
        ut = UsageType.objects.order_by('name')
    return ut


def get_negative_month_range(end_date=None):
    if end_date is None:
        end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - relativedelta(months=1)
    return date_range(start_date, end_date)


def _get_usage_value(date, usage):
    return DailyUsage.objects.filter(
        date=date, type=usage
    ).values('date').aggregate(Sum('value'))['value__sum']


def _get_usage_values_for_date_range(usage_types):
    results = OrderedDict()
    for usage in usage_types:
        results[usage] = OrderedDict()
        for date_ in get_negative_month_range():
            results[usage][date_] = _get_usage_value(
                date_, usage
            )
    return results


def _detect_missing_values(usage_values):
    missing_values = OrderedDict()
    for usage in usage_values.keys():
        for date_ in get_negative_month_range():
            if usage_values[usage][date_] is None:
                if missing_values.get(usage) is None:
                    missing_values[usage] = []
                missing_values[usage].append(date_)
    return missing_values


def _detect_big_changes(usage_values):
    changes = []
    delta = datetime.timedelta(days=1)
    for usage in usage_values.keys():
        for date_ in get_negative_month_range():
            next_date = date_ + delta
            if (usage_values[usage].get(date_) is None or
                    usage_values[usage].get(next_date) is None):
                continue
            uc1 = usage_values[usage][date_]
            uc2 = usage_values[usage][next_date]
            # XXX
            # relative_change = round(abs(uc1 - uc2) / max(uc1, uc2), 2)
            relative_change = round((uc2 - uc1) / uc1, 2)
            if abs(relative_change) > DIFF_TOLERANCE:
                changes.append((usage, date_, next_date, relative_change))
    return changes


def _detect_anomalies(usage_types):
    usage_values = _get_usage_values_for_date_range(usage_types)
    missing_values = _detect_missing_values(usage_values)
    big_changes = _detect_big_changes(usage_values)
    return (missing_values, big_changes)


def _group_by_type(big_changes):
    big_changes_by_type = OrderedDict()
    for bc in big_changes:
        if big_changes_by_type.get(bc[0]) is None:
            big_changes_by_type[bc[0]] = []
        big_changes_by_type[bc[0]].append(tuple(bc[1:]))
    return big_changes_by_type


def _merge_and_group_by_owner(usage_types, missing_values, big_changes_by_type):  # noqa: E501
    merged_anomalies = OrderedDict()
    for usage in usage_types:
        big_changes = big_changes_by_type.get(usage)
        missing_values_ = missing_values.get(usage)
        if big_changes is None and missing_values is None:
            continue
        merged_anomalies[usage] = {
            'big_changes': big_changes,
            'missing_values': missing_values_,
        }
    return merged_anomalies


def _send_notifications(anomalies):
    template_name = 'scrooge_detect_usage_anomalies_template.txt'  # XXX
    context = {'owner_name': 'John Doe'}  # XXX
    txt_content = render_to_string(template_name, context)
    print(txt_content)  # XXX
    pprint_anomalies(anomalies)  # XXX


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            dest='usage_names',  # XXX what about using symbols here..?
            action='append',
            type=str,
            default=[],
            help=(
                "UsageType names to be taken into account (by default, all "
                "are taken)."
            )
        )
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            default=False,
            help="Don't send any notifications"
        )

    def handle(self, usage_names, dry_run, *args, **options):
        """
        * missing_values:
        OrderedDict({
            UsageType: [datetime.date, ...]
        })

        * big_changes:
        [(UsageType, datetime.date1, datetime.date2, value or None), ...]

        * big_changes_by_type:
        OrderedDict({
            UsageType: [(datetime.date1, datetime.date2, value or None), ...]
        })
        """
        usage_types = get_usage_types(usage_names)
        missing_values, big_changes = _detect_anomalies(usage_types)
        big_changes_by_type = _group_by_type(big_changes)
        anomalies_to_report = _merge_and_group_by_owner(
            usage_types, missing_values, big_changes_by_type
        )
        pprint_anomalies(anomalies_to_report)
        if not dry_run:
            _send_notifications(anomalies_to_report)


def pprint_anomalies(anomalies):
    """XXX This is just a temporary function for debugging/development."""
    for k, v in anomalies.items():
        print("==========")
        print(k.name)
        print("--- Missing values:")
        for mv in v['missing_values']:
            print(mv)
        print("--- Big changes:")
        for bc in v['big_changes']:
            print("{} | {} | {:+.2%}".format(bc[0], bc[1], bc[2]))
