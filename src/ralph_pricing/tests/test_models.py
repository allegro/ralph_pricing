# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing import models


class TestModels(TestCase):
    def test_device_model(self):
        device = models.Device(device_id=3)
        device.save()
        device = models.Device.objects.get(device_id=3)
        self.assertEquals(device.device_id, 3)

    def test_venture_model(self):
        venture = models.Venture(venture_id=3)
        venture.save()
        venture = models.Venture.objects.get(venture_id=3)
        self.assertEquals(venture.venture_id, 3)

    def test_dailypart_model(self):
        device = models.Device(device_id=2)
        device.save()
        part = models.DailyPart(
            asset_id =4,
            pricing_device=device,
            date=datetime.date(2013, 4, 25),
            name='ziew',
            price=5,
        )
        part.save()
        self.assertEquals(part.date, datetime.date(2013, 4, 25))
        self.assertEquals(part.pricing_device.device_id, 2)
        self.assertEquals(part.asset_id, 4)
        self.assertEquals(part.price, 5)

    def test_dailydevice_model(self):
        device = models.Device(device_id=2)
        device.save()
        daily = models.DailyDevice(
            pricing_device=device,
            date=datetime.date(2013, 4, 25),
            name='ziew',
        )
        daily.save()
        self.assertEquals(daily.date, datetime.date(2013, 4, 25))
        self.assertEquals(daily.pricing_device.device_id, 2)

    def test_usage_models(self):
        type_ = models.UsageType(name='ziew')
        type_.save()
        price = models.UsagePrice(
            type=type_,
            price=3,
            start=datetime.date(2013, 4, 24),
            end=datetime.date(2013, 4, 26),
        )
        price.save()
        usage = models.DailyUsage(
            date=datetime.date(2013, 4, 25),
            value=3,
            type=type_,
        )
        usage.save()
        self.assertEquals(usage.value, 3)
        self.assertEquals(usage.type, type_)
        self.assertEquals(price.price, 3)
        self.assertEquals(type_.name, 'ziew')

    def test_extra_cost_models(self):
        type_ = models.ExtraCostType(name='ziew')
        type_.save()
        venture = models.Venture(venture_id=3)
        venture.save()
        cost = models.ExtraCost(
            type=type_,
            start=datetime.datetime(2013, 4, 24),
            end=datetime.datetime(2013, 4, 26),
            price=3,
            pricing_venture=venture,
        )
        cost.save()
        self.assertEquals(type_.name, 'ziew')
        self.assertEquals(venture.venture_id, 3)
        self.assertEquals(cost.type, type_)
        self.assertEquals(cost.start, datetime.datetime(2013, 4, 24))
        self.assertEquals(cost.end, datetime.datetime(2013, 4, 26))
        self.assertEquals(cost.price, 3)
        self.assertEquals(cost.pricing_venture, venture)

