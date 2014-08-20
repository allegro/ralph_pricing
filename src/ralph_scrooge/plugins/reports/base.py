# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
from collections import defaultdict
from decimal import Decimal as D

from django.db.models import Sum
from ralph_scrooge.utils import memoize

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.models import UsageType
from ralph_scrooge.plugins.base import BasePlugin

logger = logging.getLogger(__name__)


class NoPriceCostError(Exception):
    """
    Raised when price is not defined for specified date.
    """
    pass


class MultiplePriceCostError(Exception):
    """
    Raised when multiple prices are defined for specified date.
    """


class BaseReportPlugin(BasePlugin):

    def run(self, type='costs', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()
