# -*- coding: utf-8 -*-
"""
Temporary script to test memory usage and overall performance of different ways
of building DailyCosts. This file will be removed in final wersion of PR.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cProfile
import gc
import time
from datetime import date
from decimal import Decimal as D
from functools import wraps
from optparse import make_option
from random import randint

from django.core.management.base import BaseCommand
try:
    from memory_profiler import profile
except ImportError:  # for travis etc
    def profile(func):
        return func

from ralph_scrooge.models import DailyCost


def memory_profile(func):
    f = profile(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def profileit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".profile"
        prof = cProfile.Profile()
        retval = prof.runcall(profile(func), *args, **kwargs)
        prof.dump_stats(datafn)
        return retval

    return wrapper


def calc_time(func):
    def wrap(*args, **kwargs):
        gc.collect()
        started_at = time.time()
        result = func(*args, **kwargs)
        print('{} time: {}'.format(func.__name__, time.time() - started_at))
        return result
    return wrap

global_params = {
    'date': date.today(),
}


def _generate_sample(n):
    result = []
    for i in range(n):
        se_id = randint(1, 100)
        result.append({
            'service_environment_id': se_id,
            'value': 20,
            'cost': D('200'),
            'type_id': randint(1, 50),
            '_children': [
                {
                    'service_environment_id': se_id,
                    'value': 10,
                    'cost': D('100'),
                    'type_id': randint(1, 50),
                },
                {
                    'service_environment_id': se_id,
                    'value': 10,
                    'cost': D('100'),
                    'type_id': randint(1, 50),
                    '_children': [
                        {
                            'service_environment_id': se_id,
                            'value': 10,
                            'cost': D('100'),
                            'type_id': randint(1, 50),
                        }
                    ]
                }
            ]
        })
    return result


# @profileit
@calc_time
@memory_profile
def use_django_model(sample):
    print('a')
    result = DailyCost._build_tree_djangoobject(sample, **global_params)
    print(len(result))
    # print(result[0])


# profileit
@calc_time
@memory_profile
def use_namedtuple(sample):
    print('a')
    result = DailyCost._build_namedtuples(sample, **global_params)
    print(len(result))
    print(result[0])


# profileit
@calc_time
@memory_profile
def use_attribute_dict(sample):
    print('a')
    result = DailyCost._build_attrdict(sample, **global_params)
    print(len(result))
    print(result[0])


class Command(BaseCommand):
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-n',
            dest='samples_count',
            default=100,
            type=int,
        ),
    )

    def handle(self, samples_count, *args, **options):
        sample = _generate_sample(samples_count)
        use_django_model(sample)
        use_attribute_dict(sample)
        use_namedtuple(sample)
