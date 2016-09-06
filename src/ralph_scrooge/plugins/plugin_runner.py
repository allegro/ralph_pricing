#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is copy of ralph.util.plugin. In the future it could be refactored to
something more object-oriented.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


PLUGINS_BY_NAME = {}
PLUGINS_BY_REQUIREMENTS = {}
PLUGINS_BY_PRIORITIES = {}


def register(func=None, chain="default", requires=None, priority=None):
    """
    A decorator that registers a function as plugin.
    """
    if func is None:
        def wrapper(f):
            return register(func=f, chain=chain,
                            requires=requires, priority=priority)
        return wrapper
    if not requires:
        requires = set()
    PLUGINS_BY_NAME.setdefault(chain, {})[func.func_name] = func
    PLUGINS_BY_REQUIREMENTS.setdefault(
        chain,
        {},
    ).setdefault(
        frozenset(requires),
        [],
    ).append(func.func_name)
    PLUGINS_BY_PRIORITIES.setdefault(chain, {})[func.func_name] = (
        priority or 100
    )
    return func


def get_possible_plugins(chain, done_reqs):
    """
    Return a list of plugins that can be run given the list of plugins
    that has already been ran.
    """
    ret = set()
    if chain not in PLUGINS_BY_REQUIREMENTS:
        return ret
    done_reqs = set(done_reqs)
    for needed_reqs, plugins in PLUGINS_BY_REQUIREMENTS[chain].iteritems():
        if needed_reqs <= done_reqs:
            ret |= set(plugins)
    return ret


def next(chain, done_reqs):
    # TODO: deprecation log
    return get_possible_plugins(chain, done_reqs)


def run_plugin(chain, func_name, **kwargs):
    """
    Run a single plugin by a name.
    """
    return PLUGINS_BY_NAME[chain][func_name](**kwargs)


def run(chain, func_name, **kwargs):
    # TODO: add deprecation log
    return run_plugin(chain, func_name, **kwargs)


def highest_priority(chain, plugins):
    """
    Selects a plugin from given `plugins` on a specified `chain` with the
    highest priority.
    """
    ret = max(
        plugins,
        key=lambda p: PLUGINS_BY_PRIORITIES.get(chain, {}).get(p, 100)
    )
    return ret
