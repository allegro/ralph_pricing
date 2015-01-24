# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime

from django.test import TestCase

from ralph_scrooge.utils.common import HashableDict

logging.disable(logging.CRITICAL)


class ScroogeTestCaseMixin(object):
    maxDiff = None

    def _fix_dates(self, date1, date2):
        if isinstance(date1, datetime) and isinstance(date2, datetime):
            # fix for mysql - doesn't store microseconds part of datetime
            date1 = date1.replace(microsecond=0)
            date2 = date2.replace(microsecond=0)
        return date1, date2

    def assertEqual(self, *args):
        return super(ScroogeTestCaseMixin, self).assertEqual(
            *self._fix_dates(*args)
        )

    def assertGreaterEqual(self, *args):
        return super(ScroogeTestCaseMixin, self).assertGreaterEqual(
            *self._fix_dates(*args)
        )

    def _list2set(self, d):
        """
        Change all list to frozensets
        """
        if isinstance(d, dict):
            for k, v in d.iteritems():
                d[k] = self._list2set(v)
        elif isinstance(d, list):
            return frozenset(map(self._list2set, d))
        return d

    def assertNestedDictsEqual(self, el1, el2):
        """
        Test nested dicts equality by changing them to HashableDict (dict,
        which could be element of a set) and changing all list to frozenset
        (to don't compare order) - useful when comparing with QuerySets, which
        could have random order.
        """
        return self.assertEqual(
            self._list2set(HashableDict.parse(dict(el1))),
            self._list2set(HashableDict.parse(dict(el2)))
        )


class ScroogeTestCase(ScroogeTestCaseMixin, TestCase):
    pass
