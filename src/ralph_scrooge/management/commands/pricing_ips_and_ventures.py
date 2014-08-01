# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util.api_pricing import get_ip_addresses
from ralph_scrooge.management.commands._pricing_base import PricingBaseCommand
from ralph_scrooge.models import Venture


logger = logging.getLogger(__name__)


class Command(PricingBaseCommand):
    """Retrieve data for pricing for base"""
    HEADERS = ['IP', 'Venture']

    def get_data(self, *args, **options):
        """
        Collect ips matched with ventures from ralph.

        :param string file_path: path to file
        """
        results = []
        ips_and_ids, venture_ids = self.get_ips_and_venture_ids()
        ids_and_names = self.get_venture_ids_and_names(venture_ids)

        for ip, venture in ips_and_ids.iteritems():
            if venture:
                ips_and_ids[ip] = ids_and_names[venture]
            results.append([ip, ips_and_ids[ip]])

        return results

    def get_venture_ids_and_names(self, venture_ids):
        """
        Generate list with venture ids and names

        :param list venture_ids: Options from optparse
        :returns dict: list of venture ids and names
        :rtype dict:
        """
        ids_and_names = {}
        for venture in Venture.objects.filter(venture_id__in=venture_ids):
            ids_and_names[venture.venture_id] = venture.name
        return ids_and_names

    def get_ips_and_venture_ids(self):
        """
        Based on ralph, create list with key as ip and value as venture id

        :returns tuple: list of ips and venture ids and list with only ids
        :rtype tuple:
        """
        ips_and_venture_ids = {}
        venture_ids = set()

        for ip, venture in get_ip_addresses(True).iteritems():
            venture_ids.add(venture)
            ips_and_venture_ids[ip] = venture

        return ips_and_venture_ids, venture_ids
