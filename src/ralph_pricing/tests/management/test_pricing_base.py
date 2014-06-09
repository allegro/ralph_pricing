# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import patch, MagicMock

from django.test import TestCase

from ralph_pricing.management.commands.pricing_base import PricingBaseCommand


class TestPricingBaseCommand(TestCase):
    TEMPLATES = {'csv': 'T0 {0}', 'default': 'T1: {0}'}
    CSV_HEADERS = ['Header0']
    RESULTS = ['test']
    FILE_PATH = 'file_path'

    def test_get_template_csv_template(self):
        self._get_template_setup()
        self.assertEqual(
            (
                self.TEMPLATES['csv'],
                [self.TEMPLATES['csv'].format(*self.CSV_HEADERS)]
            ),
            PricingBaseCommand()._get_template({'csv_format': True})
        )

    def test_get_template_default_template(self):
        self._get_template_setup()
        self.assertEqual(
            (self.TEMPLATES['default'], []),
            PricingBaseCommand()._get_template({'csv_format': None})
        )

    @patch.object(PricingBaseCommand, '_render_to_file', MagicMock())
    def test_render_when_file_path(self):
        pricing_base_command = PricingBaseCommand()
        pricing_base_command.render(self.RESULTS, self.FILE_PATH)
        pricing_base_command._render_to_file.assert_called_once_with(
            self.RESULTS,
            self.FILE_PATH,
        )

    @patch.object(PricingBaseCommand, '_render_on_screen', MagicMock())
    def test_render(self):
        pricing_base_command = PricingBaseCommand()
        pricing_base_command.render(self.RESULTS, None)
        pricing_base_command._render_on_screen.assert_called_once_with(
            self.RESULTS,
        )

    @patch('__builtin__.open')
    def test_get_render_to_file(self, open_mock):
        pricing_base_command = PricingBaseCommand()
        pricing_base_command._render_to_file(
            self.RESULTS,
            self.FILE_PATH,
        )
        open_mock.assert_called_once_with(self.FILE_PATH, 'a+')
        open_mock().__enter__().write.assert_called_once_with(
            self.RESULTS[0] + '\n',
        )

    @patch('__builtin__.print')
    def test_render_on_screen(self, print_mock):
        PricingBaseCommand()._render_on_screen(self.RESULTS)
        print_mock.assert_called_once_with(self.RESULTS[0])

    def _get_template_setup(self):
        PricingBaseCommand.TEMPLATES = self.TEMPLATES
        PricingBaseCommand.CSV_HEADERS = self.CSV_HEADERS
