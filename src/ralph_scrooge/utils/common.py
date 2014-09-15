# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps

from django.conf import settings
from lck.cache import memoize as memoize_orig


class AttributeDict(dict):
    """
    Attribute dict. Used to attribute access to dict
    """
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


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


def memoize_proxy(func=None, *rargs, **rkwargs):
    """
    Memoize decorator proxy (not-caching)
    """
    if func is None:
        def wrapper(f):
            return memoize_proxy(func=f, *rargs, **rkwargs)
        return wrapper

    @wraps(func)
    def wrapper_standard(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper_standard

# if in testing environment (ex unit tests), set memoize decorator to memoize
# proxy, else to original (caching) memoize
memoize = memoize_proxy if getattr(settings, 'TESTING', None) else memoize_orig
