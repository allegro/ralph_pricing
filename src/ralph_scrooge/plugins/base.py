# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import re

from ralph_scrooge.utils.common import memoize

from ralph.util import plugin
from ralph_scrooge.models import Warehouse

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def camel_case_to_underscore(name):
    """
    Transform camel case string to underscore
    """
    s1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return str(ALL_CAP_RE.sub(r'\1_\2', s1).lower())


def register(*rargs, **rkwargs):
    """
    Allow to register class as ralph plugin. Class should have argumentless
    constructor and should be callable.
    """
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
    @memoize(skip_first=True)
    def get_warehouses(cls, show_in_report=True):
        """
        Returns available warehouses
        """
        warehouses = Warehouse.objects.filter()
        if show_in_report is not None:
            warehouses = warehouses.filter(show_in_report=show_in_report)
        return warehouses
