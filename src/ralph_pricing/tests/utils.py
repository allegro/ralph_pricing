import datetime
from decimal import Decimal as D

from ralph_pricing.models import (
    Device,
    Venture,
    ExtraCostType,
    DailyExtraCost,
)


def get_or_create_device(name=None, device_id=None):
    device_id = device_id if device_id else Device.objects.all().count()
    name = name if name else "Default{0}".format(device_id)
    return Device.objects.get_or_create(name=name, device_id=device_id)[0]


def get_or_create_venture(name=None, venture_id=None):
    venture_id = venture_id if venture_id else Venture.objects.all().count()
    name = name if name else "Default{0}".format(venture_id)
    return Venture.objects.get_or_create(name=name, venture_id=venture_id)[0]


def get_or_create_extra_cost_type(name=None):
    if not name:
        name = "Default{0}".format(ExtraCostType.objects.all().count())
    return ExtraCostType.objects.get_or_create(name=name)[0]


def get_or_create_daily_extra_cost(
    date=None,
    venture=None,
    type=None,
    value=None,
):
    date = date if date else datetime.date(year=2014, month=5, day=1)
    venture = venture if venture else get_or_create_venture()
    type = type if type else get_or_create_extra_cost_type()
    value = value if value else D(100)
    return DailyExtraCost.objects.get_or_create(
        date=date,
        pricing_venture=venture,
        type=type,
        value=value,
    )[0]
