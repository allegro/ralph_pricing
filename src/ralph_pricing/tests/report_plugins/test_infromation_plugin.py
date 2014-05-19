# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.plugins.reports.deprecation import Deprecation


class TestInformationPlugin(TestCase):
    def setUp(self):
        # ventures
        self.venture1 = models.Venture(venture_id=1, name='V1', is_active=True)
        self.venture1.save()
        self.venture2 = models.Venture(venture_id=2, name='V2', is_active=True)
        self.venture2.save()
        self.venture3 = models.Venture(venture_id=3, name='V3', is_active=True)
        self.venture3.save()
        self.ventures_subset = [self.venture1, self.venture2]
        self.ventures = models.Venture.objects.all()

        # devices
        # add i*5 devices for each venture
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        i = 1
        for j, venture in enumerate(self.ventures):
            for k in range((j + 1) * 5):
                # add device
                d = models.Device(
                    name='Device{0}'.format(i),
                    device_id=i,
                )
                d.save()
                for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                    dd = models.DailyDevice(
                        date=day,
                        name='Device{0}'.format(i),
                        price=100*i,
                        deprecation_rate=0.25,
                        is_deprecated=False,
                        pricing_venture=venture,
                        pricing_device=d,
                    )
                    dd.save()
                    i += 1

    def test_costs(self):
        pass

    def test_costs_per_device(self):
        pass
