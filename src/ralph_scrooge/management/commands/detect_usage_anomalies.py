# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import OrderedDict
from smtplib import SMTPException

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.loader import render_to_string

from ralph_scrooge.models import UsageType, DailyUsage
# TODO(xor-xor): Consider moving `date_range` to some utils module.
from ralph_scrooge.rest.service_environment_costs import date_range


log = logging.getLogger(__name__)
yesterday = datetime.date.today() - datetime.timedelta(days=1)

# XXX This could be overridden on per-UsageType basis (e.g. in some dict loaded
# from settings).
DIFF_TOLERANCE = 0.2
NOTIFY_THRESHOLDS = [datetime.timedelta(days=d) for d in (1, 7, 14)]


def get_usage_types(symbols):
    if symbols:
        uts = UsageType.objects.filter(symbol__in=symbols).order_by('symbol')
        known_symbols = [ut.symbol for ut in uts]
        unknown_symbols = []
        for s in symbols:
            if s not in known_symbols:
                unknown_symbols.append(s)
        if unknown_symbols:
            log.warning(
                "Unknown symbol(s) detected: {}. Ignoring."
                .format(", ".join(unknown_symbols))
            )
    else:
        uts = UsageType.objects.order_by('symbol')
    return uts


def get_negative_month_range(end_date):
    start_date = end_date - relativedelta(months=1)
    return date_range(start_date, end_date)


def _get_usage_value(date, usage):
    return DailyUsage.objects.filter(
        date=date, type=usage
    ).values('date').aggregate(Sum('value'))['value__sum']


def _get_usage_values_for_date_range(usage_types, end_date):
    results = {}
    start_date = get_negative_month_range(end_date).next()
    for usage in usage_types:
        results[usage] = {}
        daily_usages = dict(
            DailyUsage.objects.filter(
                date__gte=start_date, date__lte=end_date, type=usage
            ).values_list('date').annotate(Sum('value'))
        )
        results[usage].update(daily_usages)
    return results


def _detect_missing_values(usage_values, end_date):
    missing_values = {}
    for usage in usage_values.keys():
        for date in get_negative_month_range(end_date):
            if usage_values[usage].get(date) is None:
                if missing_values.get(usage) is None:
                    missing_values[usage] = []
                missing_values[usage].append(date)
    return missing_values


def _detect_big_changes(usage_values, end_date):

    def rel_change(uc1, uc2):
        ch = (uc2 - uc1) / uc1
        return round(ch, 2)

    def group_by_type(changes):
        changes_by_type = {}
        for c in changes:
            if changes_by_type.get(c[0]) is None:
                changes_by_type[c[0]] = []
            changes_by_type[c[0]].append(tuple(c[1:]))
        return changes_by_type

    changes = []
    delta = datetime.timedelta(days=1)
    for usage in usage_values.keys():
        for date in get_negative_month_range(end_date):
            next_date = date + delta
            if (usage_values[usage].get(date) is None or
                    usage_values[usage].get(next_date) is None):
                continue
            uc1 = usage_values[usage][date]
            uc2 = usage_values[usage][next_date]
            relative_change = rel_change(uc1, uc2)
            if abs(relative_change) > DIFF_TOLERANCE:
                changes.append(
                    (usage, date, next_date, uc1, uc2, relative_change)
                )
    grouped_changes = group_by_type(changes)
    return grouped_changes


def _detect_anomalies(usage_types, end_date):
    usage_values = _get_usage_values_for_date_range(usage_types, end_date)
    missing_values = _detect_missing_values(usage_values, end_date)
    big_changes = _detect_big_changes(usage_values, end_date)
    if not missing_values and not big_changes:
        return
    # Some post-processing in order to facilitate composing final e-mail(s)
    # with report(s).
    anomalies = _merge_by_type(usage_types, missing_values, big_changes)
    anomalies_to_report = _group_anomalies_by_owner(anomalies)
    return anomalies_to_report


def _merge_by_type(usage_types, missing_values, big_changes_by_type):
    merged_anomalies = {}
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


def _group_anomalies_by_owner(anomalies):
    """...and group/sort missing_values by date"""

    def group_missing_values_by_date(usage, missing_values):
        ret = {}
        for date in missing_values:
            if ret.get(date) is None:
                ret[date] = set()
            ret[date].add(usage)
        return ret

    ret = {}
    for usage in anomalies.keys():
        owners = usage.owners.all()
        if not owners.exists():
            log.warning(
                'Anomalies detected in UsageType "{}", but it doesn\'t have '
                'any owners defined, hence we cannot notify them. Please '
                'correct that ASAP.'.format(usage.name)
            )
            continue
        for owner in owners:
            if ret.get(owner) is None:
                ret[owner] = {'missing_values': {}, 'big_changes': {}}

            mv_by_date = group_missing_values_by_date(
                usage, anomalies[usage]['missing_values']
            )
            for date, ut_set in mv_by_date.items():
                mvs = ret[owner]['missing_values'].get(date)
                if mvs is None:
                    ret[owner]['missing_values'][date] = ut_set
                else:
                    ret[owner]['missing_values'][date].update(ut_set)

            big_changes = anomalies[usage]['big_changes']
            if big_changes is not None:
                ret[owner]['big_changes'][usage] = big_changes

    # Sort missing values by date for more readable output in notification.
    for owner in ret.keys():
        d = OrderedDict(
            sorted(ret[owner]['missing_values'].items())
        )
        ret[owner]['missing_values'] = d
    return ret


def _send_mail(address, html_message):
    try:
        num_msgs_sent = send_mail(
            'Scrooge notifications test',  # XXX change it
            '',  # TODO(xor-xor): Do we need plain-text version of the message?
            settings.EMAIL_NOTIFICATIONS_SENDER,
            [address],
            fail_silently=False,
            html_message=html_message,
        )
    except SMTPException as e:
        log.error(
            "Got error from SMTP server: {}: {}. E-mail addressed to {} "
            "has not been sent.".format(e.smtp_code, e.smtp_error, recipient)
        )
        return
    if num_msgs_sent == 1:
        log.info(
            "Notification e-mail to {} sent successfully.".format(address)
        )
    else:
        log.error(
            "Notification e-mail to {} couldn't be delivered. Please try "
            "again later.".format(address)
        )


def _send_notifications(anomalies):
    template_name = 'scrooge_detect_usage_anomalies_template.html'
    for recipient, anomalies_ in anomalies.items():
        context = {
            'recipient': recipient,
            'big_changes': anomalies_['big_changes'],
            'missing_values': anomalies_['missing_values'],
        }
        body = render_to_string(template_name, context)
        _send_mail(recipient.email, body)


def pprint_anomalies(anomalies):
    for user, anomalies_ in anomalies.items():
        print("-" * 79)
        print('Owner: {}'.format(user.username))
        missing_values = anomalies_['missing_values']
        if missing_values is not None:
            print('\nMissing values for days:')
            for date, usage_types in missing_values.items():
                print(
                    '{}: {}'.format(
                        date, ", ".join([ut.symbol for ut in usage_types])
                    )
                )
        big_changes = anomalies_['big_changes']
        if big_changes is not None:
            for ut, vals in big_changes.items():
                print('\nUnusual changes for {}:'.format(ut.symbol))
                for v in vals:
                    # XXX determine padding width for values dynamically
                    print(
                        "{} | {} | {: >16.2f} | {: >16.2f} | {: >+8.2%}"
                        .format(*v)
                    )


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            dest='usage_symbols',
            action='append',
            type=str,
            default=[],
            help=(
                "UsageType symbols to be taken into account (by default, all "
                "are taken)."
            )
        )
        parser.add_argument(
            '-e',
            dest='end_date',
            default=yesterday,
            help=(
                "End date of the monthly range which should be analyzed "
                "(default: yesterday). This date *is not* included in "
                "the results."
            )
        )
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            default=False,
            help="Don't send any notifications"
        )

    def handle(self, usage_symbols, dry_run, *args, **options):
        """XXX check if these descriptions are still valid
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
        def parse_date(date):
            if not isinstance(date, datetime.date):
                return datetime.datetime.strptime(date, '%Y-%m-%d').date()
            else:
                return date

        end_date = parse_date(options['end_date'])
        usage_types = get_usage_types(usage_symbols)
        anomalies = _detect_anomalies(usage_types, end_date)
        if not anomalies:
            log.info("No anomalies detected.")
            return
        if dry_run:
            pprint_anomalies(anomalies)
        else:
            _send_notifications(anomalies)
