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

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.models import UsageType
from ralph_scrooge.plugins.base import BasePlugin


logger = logging.getLogger(__name__)


class AttributeDict(dict):
    """
    Attribute dict. Used to attribute access to dict
    """
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class BaseReportPlugin(BasePlugin):
    """
    Base report plugin

    Every plugin which inherit from BaseReportPlugin should implement 3
    methods: usages, schema and total_cost.

    Usages and schema methods are connected - schema defines output format of
    usages method. Usages method should return information about usages (one
    or more types - depending on plugins needs) per every venture.
    """

    def run(self, type='costs', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()

    @abc.abstractmethod
    def costs(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def schema(self, *args, **kwargs):
        pass
