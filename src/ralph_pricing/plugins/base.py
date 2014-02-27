# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import re

from ralph.util import plugin
from ralph_pricing.models import Warehouse

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def camel_case_to_underscore(name):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return str(ALL_CAP_RE.sub(r'\1_\2', s1).lower())


def register(*rargs, **rkwargs):
    def wrap(cls):
        wrapper = cls()
        plugin.register(wrapper, *rargs, **rkwargs)
        return wrapper
    return wrap


class BasePlugin(object):
    __metaclass__ = abc.ABCMeta

    @property
    def func_name(self):
        """
        Workaround for registering class as function in plugin
        """
        return camel_case_to_underscore(self.__class__.__name__)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    @classmethod
    def get_warehouses(cls):
        return Warehouse.objects.filter(show_in_report=True)
