# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph_pricing.management.commands.pricing_base import PricingBaseCommand
from ralph.util.api_pricing import get_ip_addresses


logger = logging.getLogger(__name__)


class Command(PricingBaseCommand):
    """Retrieve data for pricing for base"""
    def handle(self, file_path, *args, **options):
        """
        Collect ips matched with ventures from ralph.

        :param string file_path: path to file
        """
        _template, results = self._get_template(options)

        for ip, venture in get_ip_addresses(True).iteritems():
            results.append(_template.format(ip, venture))

        for ip, venture in get_ip_addresses(False).iteritems():
            results.append(_template.format(ip, venture))

        self.render(results, file_path)
