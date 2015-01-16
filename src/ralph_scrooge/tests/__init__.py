# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime

from django.test import TestCase

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


class ScroogeTestCase(ScroogeTestCaseMixin, TestCase):
    pass
