# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
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
    TEMPLATES = {}
    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-c',
            dest='csv_format',
            action='store_true',
            default=False,
            help="Show results as csv file",
        ),
        make_option(
            '--file',
            dest='file_path',
            default=None,
            help="Move results to file",
        ),
    )

    @abc.abstractmethod
    def handle(self, file_path, *args, **options):
        """
        Abstract method for custom logic. This method is designated for
        collect data and create list of rows with results to print.

        :param string file_path: path to file
        """
        pass

    def _get_template(self, options):
        """
        Choose template and create results container. For example csv
        require headers.

        :param dict options: Options from optparse
        :returns tuple: choosen template and predefined results
        :rtype tuple:
        """
        csv = options.get('csv_format')
        template = self.TEMPLATES.get('csv' if csv else 'default')
        results = [template.format(*self.CSV_HEADERS)] if csv else []

        return (template, results)

    def render(self, results, file_path):
        """
        Render results to csv or console.

        :param list results: Rows to pring
        :param string file_path: path to file
        """
        if not file_path:
            self._render_on_screen(results)
        else:
            self._render_to_file(results, file_path)

    def _render_on_screen(self, results):
        """
        Print results on screen.

        :param list results: Rows to pring
        """
        for result in results:
            print (result)

    def _render_to_file(self, results, file_path):
        """
        Save results to file.

        :param list results: Rows to pring
        :param string file_path: path to file
        """
        with open(file_path, 'a+') as f:
            for result in results:
                f.write(smart_str(result + '\n'))
