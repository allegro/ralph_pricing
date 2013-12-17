# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from mock import MagicMock
import logging

from django.test import TestCase

from ralph_pricing.models import Device, DailyUsage, Venture
from ralph.util import plugin
from ralph_pricing import plugins  # noqa
from ralph_pricing.plugins.power_consumption import (
    set_usages,
    VentureNotDefinedError,
    DefinedVentureDoesNotExist,
)


class TestPowerConsumption(TestCase):
    def setUp(self):
        logging.basicConfig()

    def test_if_run_without_today_argument(self):
        success, message, context = plugin.run(
            'pricing',
            'powerconsumption',
        )
        self.assertEqual(success, False)
        self.assertEqual(message, 'Not configured.')
        self.assertEqual(context, {})

    def test_when_device_have_not_venture_symbol(self):
        self.assertRaises(
            VentureNotDefinedError,
            set_usages,
            MagicMock(venture_symbol=''),
            datetime.date.today(),
        )

    def test_if_venture_not_exist(self):
        self.assertRaises(
            DefinedVentureDoesNotExist,
            set_usages,
            MagicMock(venture_symbol='not_exist_venture'),
            datetime.date.today(),
        )

    def test_create_many_daily_usage_imprints_of_power_consumption_(self):
        self._create_ventures_and_devices(2)

        success, message, context = plugin.run(
            'pricing',
            'powerconsumption',
            today=datetime.date.today(),
        )

        self.assertEqual(len(DailyUsage.objects.all()), 2)

    def _create_ventures_and_devices(self, count):
        for i in xrange(count):
            symbol = 'test_venture_symbol_{0}'.format(i)
            self._create_venture(i, symbol)
            self._create_device(i, symbol)

    def _create_venture(self,
                        venture_id,
                        symbol='test_venture_symbol',
                        name='TestVenture'):
        Venture(venture_id=venture_id, name=name, symbol=symbol).save()

    def _create_device(self,
                       device_id,
                       venture_symbol='test_venture_symbol',
                       power_consumption=10):
        Device(
            device_id=device_id,
            venture_symbol=venture_symbol,
            power_consumption=power_consumption,
        ).save()
