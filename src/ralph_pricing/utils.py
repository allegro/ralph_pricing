# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def ranges_overlap(start1, end1, start2, end2):
    """
    Checks if two intervals are overlapping. Function requires intervals to be
    proper (end >= start). Works with any types of comparable by mathematical
    operators objects.
    """
    return start1 <= end2 and end1 >= start2
