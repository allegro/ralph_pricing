# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import csv
import sys
import logging
import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str


logger = logging.getLogger(__name__)


class PricingBaseCommand(BaseCommand):
    """
    Class contains standard options like generate to csv or generate to file.
    """
    HEADERS = []
    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '--delimiter',
            dest='delimiter',
            default=';',
            help="Move results to file",
        ),
        make_option(
            '--file_path',
            dest='file_path',
            default=None,
            help="Move results to file",
        ),
    )

    @abc.abstractmethod
    def get_data(self):
        """
        Abstract Method for collects and prepare data

        :return list results: list of lists, nested list represents single row
        """
        pass

    def get_prepared_data(self):
        """
        Prepare data for print on screen or send to client. For example
        encoding each cell.

        :return list results: list of lists, nested list represents single row
        """
        results = self.get_data()
        results.insert(0, self.HEADERS)
        for i, line in enumerate(results):
            for k, cell in enumerate(line):
                results[i][k] = smart_str(cell)
        return results

    def handle(self, delimiter, file_path, *args, **options):
        """
        Main method, use methods for colleting data and send results on screen

        :param string delimiter: Delimiter for csv format
        """
        if file_path:
            writer = csv.writer(
                open(file_path, 'w'),
                delimiter=str(delimiter),
                quoting=csv.QUOTE_MINIMAL,
            )
        else:
            writer = csv.writer(sys.stdout, delimiter=str(delimiter))
        writer.writerows(self.get_prepared_data())
