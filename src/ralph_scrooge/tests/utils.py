# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import datetime
from decimal import Decimal as D

from ralph_scrooge.models import (
    DailyDevice,
    DailyUsage,
    DailyExtraCost,
    Device,
    ExtraCostType,
    UsageType,
    Venture,
    ExtraCost,
)


def get_or_create_usage_type(name=None, **kwargs):
    usage_count = UsageType.objects.all().count()
    name = name or "Default{0}".format(usage_count)
    return UsageType.objects.get_or_create(
        name=name,
        type='SU',
    )[0]


def get_or_create_device(name=None, asset_id=None, **kwargs):
    asset_id = asset_id or Device.objects.all().count()
    name = name or "Default{0}".format(asset_id)
    return Device.objects.get_or_create(
        name=name,
        asset_id=asset_id,
        defaults=kwargs,
    )[0]


def get_or_create_venture(
    name=None,
    venture_id=None,
    is_active=True,
    **kwargs
):
    venture_id = venture_id or Venture.objects.all().count()
    name = name or "Default{0}".format(venture_id)
    return Venture.objects.get_or_create(
        name=name,
        venture_id=venture_id,
        is_active=is_active,
        defaults=kwargs,
    )[0]


def get_or_create_dailyusage(
    date=None,
    type=None,
    venture=None,
    value=None,
    **kwargs
):
    date = date or datetime.date.today()
    venture = venture or get_or_create_venture()
    type = type or get_or_create_usage_type()
    value = value or 0
    return DailyUsage.objects.get_or_create(
        date=date,
        value=value,
        pricing_venture=venture,
        type=type,
        **kwargs
    )[0]


def get_or_create_dailydevice(date=None, device=None, venture=None, **kwargs):
    date = date or datetime.date.today()
    venture = venture or get_or_create_venture()
    device = device or get_or_create_device()
    return DailyDevice.objects.get_or_create(
        date=date,
        pricing_device=device,
        pricing_venture=venture,
        **kwargs
    )[0]


def get_or_create_extra_cost_type(name=None):
    name = name or "Default{0}".format(ExtraCostType.objects.all().count())
    return ExtraCostType.objects.get_or_create(name=name)[0]


def get_or_create_extra_cost(
    mode=None,
    pricing_venture=None,
    monthly_cost=None,
    type=None,
    **kwargs
):
    pricing_venture = pricing_venture or get_or_create_venture()
    monthly_cost = monthly_cost or D(100)
    mode = mode or 0
    type = type or get_or_create_extra_cost_type()
    return ExtraCost.objects.get_or_create(
        monthly_cost=monthly_cost,
        pricing_venture=pricing_venture,
        mode=mode,
        type=type,
        defaults=kwargs,
    )[0]


def get_or_create_daily_extra_cost(
    date=None,
    venture=None,
    type=None,
    value=None,
):
    date = date or datetime.date.today()
    venture = venture or get_or_create_venture()
    type = type or get_or_create_extra_cost_type()
    value = value or D(100)
    return DailyExtraCost.objects.get_or_create(
        date=date,
        pricing_venture=venture,
        type=type,
        value=value,
    )[0]


def sample_schema():
    return [
        OrderedDict([
            ('field1', {'name': 'Field1'}),
            ('field2', {
                'name': 'Field2',
                'currency': True,
                'total_cost': True,
            }),
        ]),
        OrderedDict([
            ('field3', {'name': 'Field3'}),
            ('field4', {
                'name': 'Field4',
                'currency': True,
                'total_cost': True,
            }),
        ]),
    ]
