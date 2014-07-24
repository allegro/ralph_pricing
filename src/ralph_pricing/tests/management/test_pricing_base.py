# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from mock import patch

from django.test import TestCase

from ralph_pricing.management.commands.pricing_base import PricingBaseCommand


PricingBaseCommand.__abstractmethods__ = set()


class TestPricingBaseCommand(TestCase):
    @patch.object(PricingBaseCommand, 'get_data', lambda x: [['test']])
    def test_get_prepared_data(self):
        self.assertEqual(
            PricingBaseCommand().get_prepared_data(),
            [[], ['test']],
        )

    @patch.object(PricingBaseCommand, 'get_data', lambda x: [['test']])
    @patch('ralph_pricing.management.commands.pricing_base.UnicodeWriter')
    def test_handle_on_screen(self, writer_mock):
        PricingBaseCommand().handle(';', None)
        writer_mock.assert_called_once_with(
            sys.stdout,
            delimiter=';',
            encoding='cp1250',
        )

    @patch.object(PricingBaseCommand, 'get_data', lambda x: [['test']])
    @patch('__builtin__.open')
    @patch('ralph_pricing.management.commands.pricing_base.UnicodeWriter')
    def test_handle_to_file(self, writer_mock, open_mock):
        PricingBaseCommand().handle(';', 'test_file')
        open_mock.assert_called_once_with('test_file', 'w')
