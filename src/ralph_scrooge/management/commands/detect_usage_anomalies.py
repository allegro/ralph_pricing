# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import OrderedDict
from smtplib import SMTPException

from dateutil import relativedelta as rd
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.loader import render_to_string

from ralph_scrooge.models import (
    DailyUsage,
    UsageType,
    UsageTypeUploadFreq,
)
# TODO(xor-xor): Consider moving `date_range` to some utils module.
from ralph_scrooge.rest.service_environment_costs import date_range


class UnknownUsageTypeUploadFreqError(Exception):
    """Raised when UsageTypeUploadFreq contains a choice which is not handled
    in this module (see: `_get_max_expected_date` function).
    """
    pass


log = logging.getLogger(__name__)
a_day = datetime.timedelta(days=1)
yesterday = datetime.date.today() - a_day

# XXX Move this to UsageType as `change_tolerance` field, or something like
# that.
DIFF_TOLERANCE = 0.2


def get_usage_types(symbols):
    """Fetch UsageTypes for `symbols` and report unknown ones. If `symbols` is
    given as an empty list, fetch all UsageTypes instead.
    """
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
    """Return an iterator yielding dates starting from end_date - month and
    ending at end_date - 1 day, e.g:
    for end_date = datetime.date(2016, 11, 5) you will get:
    datetime.date(2016, 10, 5),
    datetime.date(2016, 10, 6),
    ...
    datetime.date(2016, 11, 4).
    """
    start_date = end_date - relativedelta(months=1)
    return date_range(start_date, end_date)


def _get_usage_values_for_month(usage_types, end_date):
    """Aggregate values of `usage_types` per day within a month range
    designated by (`end_date` - 1 month, `end_date`), where `end_date` is not
    included. If there are no values for given UsageType/day, it will be
    omitted.
    """
    results = {}
    start_date = get_negative_month_range(end_date + a_day).next()
    for usage in usage_types:
        results[usage] = {}
        daily_usages = dict(
            DailyUsage.objects.filter(
                date__gte=start_date, date__lte=end_date, type=usage
            ).values_list('date').annotate(Sum('value'))
        )
        results[usage].update(daily_usages)
    return results


def _get_max_expected_date(usage, date):
    """Calculate max expected date for given `date` and upload frequency for
    given `usage`. Raises UnknownUsageTypeUploadFreqError if `usage` has an
    upload frequency that's not handled here.
    """
    freq_name = UsageTypeUploadFreq.from_id(usage.upload_freq).name
    freq_margin = UsageTypeUploadFreq.from_id(usage.upload_freq).margin
    if freq_name == 'daily':
        max_date = date - freq_margin
    elif freq_name == 'weekly':
        max_date = date - freq_margin + relativedelta(weekday=rd.SU(-1))
    elif freq_name == 'monthly':
        if date.day == freq_margin.days:
            max_date = date - freq_margin
        else:
            max_date = date - freq_margin + relativedelta(day=1, days=-1)
    else:
        # This shouldn't happen...
        raise UnknownUsageTypeUploadFreqError()
    return max_date


def _detect_missing_values(usage_values, end_date):
    """Find missing dates in `usage_values` within a month range given by
    `get_negative_month_range` and return them as a dict keyed by UsageTypes,
    where values are lists of those missing dates.

    The values (dates) that are outside of the margin defined by
    UsageTypeUploadFreq are filtered out from the final dict.
    """
    missing_values = {}
    for usage in usage_values.keys():
        max_date = _get_max_expected_date(usage, end_date)
        for date in get_negative_month_range(end_date + a_day):
            if (usage_values[usage].get(date) is None and not date > max_date):
                if missing_values.get(usage) is None:
                    missing_values[usage] = []
                missing_values[usage].append(date)
    return missing_values


def _detect_unusual_changes(usage_values, end_date):
    """Having `usage_values` like:

    {<UsageType: some usage 1>: {datetime.date(2016, 10, 5): 10.00,
                                 datetime.date(2016, 10, 6): 15.00,
                                 datetime.date(2016, 10, 7): 99.00},
     <UsageType: some usage 2>: { ... }}

    ...iterate over them and compare values in each pair of adjoining days. If
    such change is bigger than DIFF_TOLERANCE, record it as a change that has
    to be reported, e.g.:


    {<UsageType: some usage 1>: (datetime.date(2016, 10, 6),
                                 datetime.date(2016, 10, 7),
                                 15.00,
                                 99.00,
                                 5.6)}

    (the last value in the tuple above is the relative change between 15.00
    and 99.00)
    """

    def get_relative_change(val1, val2):
        ch = (val2 - val1) / val1
        return round(ch, 2)

    def group_by_type(changes):
        """Having a list of tuples like:
        (<UsageType>, datetime.date, datetime.date, float, float, float)
        ...group them in a dict by <UsageType>, removing <UsageType> element
        from all tuples.
        """
        changes_by_type = {}
        for c in changes:
            if changes_by_type.get(c[0]) is None:
                changes_by_type[c[0]] = []
            changes_by_type[c[0]].append(tuple(c[1:]))
        return changes_by_type

    changes = []
    delta = datetime.timedelta(days=1)
    for usage in usage_values.keys():
        for date in get_negative_month_range(end_date + a_day):
            next_date = date + delta
            if (usage_values[usage].get(date) is None or
                    usage_values[usage].get(next_date) is None):
                continue
            uv1 = usage_values[usage][date]
            uv2 = usage_values[usage][next_date]
            relative_change = get_relative_change(uv1, uv2)
            if abs(relative_change) > DIFF_TOLERANCE:
                changes.append(
                    (usage, date, next_date, uv1, uv2, relative_change)
                )
    grouped_changes = group_by_type(changes)
    return grouped_changes


def _detect_anomalies(usage_types, end_date):
    """Glues together individual steps of anomaly detection and perform
    some post-processing on their result in order to facilitate composing
    final e-mails with anomaly reports.
    """
    usage_values = _get_usage_values_for_month(usage_types, end_date)
    missing_values = _detect_missing_values(usage_values, end_date)
    unusual_changes = _detect_unusual_changes(usage_values, end_date)
    if not missing_values and not unusual_changes:
        return
    # Post-processing.
    anomalies = _merge_by_type(usage_types, missing_values, unusual_changes)
    anomalies_to_report = _group_anomalies_by_owner(anomalies)
    return anomalies_to_report


def _merge_by_type(usage_types, missing_values, unusual_changes_by_type):
    """Merge the contents of dicts `missing_values` and
    `unusual_changes_by_type`. The result will have the following form:
    {
        <UsageType>: {
            'unusual_changes': [
                (datetime.date, datetime.date, float, float, float),
                ...
             ],
            'missing_values': [
                datetime.date,
                ...
            ],
        },
    }
    """
    merged_anomalies = {}
    for usage in usage_types:
        unusual_changes = unusual_changes_by_type.get(usage)
        missing_values_ = missing_values.get(usage)
        if unusual_changes is None and missing_values is None:
            continue
        merged_anomalies[usage] = {
            'unusual_changes': unusual_changes,
            'missing_values': missing_values_,
        }
    return merged_anomalies


def _group_anomalies_by_owner(anomalies):
    """Having `anomalies` in form described in `_merge_by_type`, group them by
    owner of given UsageType:

    {
        <ScroogeUser>: {
            'unusual_changes': {
                <UsageType>: [
                    (datetime.date, datetime.date, float, float, float),
                    ....
                ]
            },
            'missing_values': OrderedDict([
                (datetime.date, set([<UsageType>])),
                ...
            ]),
        }
        ...
    }

    This function also groups missing values by date and sorts them for more
    readable output in notification.

    If some UsageType has multiple owners, then each one of them will have
    relevant entries duplicated.
    """

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
                ret[owner] = {'missing_values': {}, 'unusual_changes': {}}

            mv_by_date = group_missing_values_by_date(
                usage, anomalies[usage]['missing_values']
            )
            for date, ut_set in mv_by_date.items():
                mvs = ret[owner]['missing_values'].get(date)
                if mvs is None:
                    ret[owner]['missing_values'][date] = ut_set
                else:
                    ret[owner]['missing_values'][date].update(ut_set)

            unusual_changes = anomalies[usage]['unusual_changes']
            if unusual_changes is not None:
                ret[owner]['unusual_changes'][usage] = unusual_changes

    # Sort missing values by date.
    for owner in ret.keys():
        d = OrderedDict(
            sorted(ret[owner]['missing_values'].items())
        )
        ret[owner]['missing_values'] = d
    return ret


def _send_mail(address, html_message):
    """Basically, a wrapper around Django's own `send_mail` with error-checking
    and logging added.
    """
    try:
        num_msgs_sent = send_mail(
            (
                '[test] Unusual changes / missing values for your usage '
                'type(s) in Scrooge'
            ),  # XXX remove "[test]" prefix
            '',  # TODO(xor-xor): Do we need plain-text version of the message?
            settings.EMAIL_NOTIFICATIONS_SENDER,
            [address],
            fail_silently=False,
            html_message=html_message,
        )
    except SMTPException as e:
        if hasattr(e, 'smtp_error') and hasattr(e, 'smtp_code'):
            msg_substr = "{}: {}".format(e.smtp_code, e.smtp_error)
        else:
            msg_substr = e.message.rstrip('.')
        log.error(
            "Got error from SMTP server: {}. E-mail addressed to {} "
            "has not been sent.".format(msg_substr, address)
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
    """For each owner/anomalies pair from `anomalies`, send e-mail notification
    to owner about anomalies detected in his/her UsageTypes.
    """
    template_name = 'scrooge_detect_usage_anomalies_template.html'
    for recipient, anomalies_ in anomalies.items():
        context = {
            'recipient': recipient,
            'unusual_changes': anomalies_['unusual_changes'],
            'missing_values': anomalies_['missing_values'],
            'site_url': settings.BASE_MAIL_URL,
        }
        body = render_to_string(template_name, context)
        _send_mail(recipient.email, body)


def pprint_anomalies(anomalies):
    """Pretty-printing for `--dry-run` switch and for debugging."""
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
        unusual_changes = anomalies_['unusual_changes']
        if unusual_changes is not None:
            for ut, vals in unusual_changes.items():
                print('\nUnusual changes for {}:'.format(ut.symbol))
                for v in vals:
                    # TODO(xor-xor): Determine width for 3rd and 4th columns
                    # dynamically here.
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
                "(default: yesterday)."
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
