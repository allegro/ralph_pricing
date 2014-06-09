# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import Mock

from django.test import TestCase

from ralph_pricing.management.commands import pricing_ips_and_ventures
from ralph_pricing.management.commands.pricing_ips_and_ventures import (
    Command
)
from ralph_pricing.tests import utils


class TestPricingIpsWithoutVentureCommand(TestCase):
    def setUp(self):
        utils.get_or_create_venture()
        utils.get_or_create_venture()
        pricing_ips_and_ventures.get_ip_addresses = Mock(
            return_value={'0.0.0.0': None}
        )

    def test_get_venture_ids_and_names(self):
        self.assertEqual(
            Command().get_venture_ids_and_names([0]),
            {0: u'Default0'},
        )

    def test_get_ips_and_venture_ids(self):
        self.assertEqual(
            Command().get_ips_and_venture_ids(),
            ({u'0.0.0.0': None}, set([None])),
        )

    def test_handle_when_venture_is_none(self):
        Command.render = Mock()
        Command().handle(None)
        Command.render.assert_called_once_with(
            [u'IP: 0.0.0.0, Venture: None'],
            None
        )

    def test_handle(self):
        pricing_ips_and_ventures.get_ip_addresses = Mock(
            return_value={'0.0.0.0': 1}
        )
        Command.render = Mock()
        Command().handle(None)
        Command.render.assert_called_once_with(
            [u'IP: 0.0.0.0, Venture: Default1'],
            None
        )
