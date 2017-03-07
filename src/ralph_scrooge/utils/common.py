# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from datetime import datetime
from decimal import Decimal

from django.conf import settings
# DEPRECATED. Import memoize directly from `ralph_scrooge.cache`
from ralph_scrooge.utils.cache import memoize  # noqa: F401


class AttributeDict(dict):
    """
    Attribute dict. Used to attribute access to dict
    """
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class HashableDict(dict):
    """
    Dict that could be used as element in set (thus it's immutable). Should
    only be used to comparisons etc.
    """

    @classmethod
    def parse(cls, el):
        """
        Convert all dicts to HashableDicts in nested structure.
        """
        if isinstance(el, list):
            for i, x in enumerate(el):
                el[i] = HashableDict.parse(x)
        elif isinstance(el, dict):
            d = HashableDict()
            for k, v in el.iteritems():
                d[k] = HashableDict.parse(v)
            return d
        return el

    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


def get_cache_name(*names):
    for name in names:
        if name in settings.CACHES:
            return name
    return 'default'


def get_queue_name(*names):
    for name in names:
        if name in settings.RQ_QUEUES:
            return name
    return 'default'


def ranges_overlap(start1, end1, start2, end2):
    """
    Checks if two intervals are overlapping. Function requires intervals to be
    proper (end >= start). Works with any types of comparable by mathematical
    operators objects.
    """
    return start1 <= end2 and end1 >= start2


def sum_of_intervals(intervals):
    """
    Returns (list of) sum of intervals. Intervals could be tuple of any
    orderable values (ex. integers, dates). If sets are overlapping, they are
    "merged" together and resulting interval is (min(start1, start2),
    max(end1, end2)).

    >>> sum_of_intervals([(1, 5), (4, 10), (7, 13), (15, 20), (21, 30)])
    [(1, 13), (15, 20), (21, 30)]
    """
    intervals_set = set()
    for v_start, v_end in intervals:
        intervals_set.add((v_start, True))
        intervals_set.add((v_end, False))
    intervals = list(intervals_set)
    intervals.sort(key=lambda a: a[0])

    current_start = None
    started = 0
    result = []
    for value, is_start in intervals:
        if is_start:
            if current_start is None:
                current_start = value
            started += 1
        else:
            started -= 1
            if started == 0:
                result.append((current_start, value))
                current_start = None
    return result


def normalize_decimal(d):
    """
    Normalize decimal without scientific notation (remove exponent and trailing
    zeros).

    Source: https://docs.python.org/2/library/decimal.html#decimal-faq

    >>> normalize_decimal(Decimal('11.00000'))
    Decimal('11')
    >>> normalize_decimal(Decimal('11.11000'))
    Decimal('11.11')
    >>> normalize_decimal(Decimal('11E2'))
    Decimal('1100')
    """
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


def validate_date(date_):
    try:
        return datetime.strptime(date_, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid date: '{}'.".format(date_)
        )
