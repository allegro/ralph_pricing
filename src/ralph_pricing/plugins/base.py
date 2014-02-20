# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from ralph.util import plugin

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_case_to_underscore(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def register(*rargs, **rkwargs):
    def wrap(cls):
        def wrapper(*args, **kwargs):
            return cls()(*args, **kwargs)
        wrapper.__name__ = camel_case_to_underscore(cls.__name__)
        plugin.register(wrapper, *rargs, **rkwargs)
        return wrapper
    return wrap


class BasePlugin(object):
    __metaclass__ = abc.ABCMeta

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass
