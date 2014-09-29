# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
import textwrap
from optparse import make_option

from bob.csvutil import UnicodeWriter
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)

DEFAULT_ENCODING = 'utf-8'
DEFAULT_CSV_ENCODING = 'cp1250'


class ScroogeBaseCommand(BaseCommand):
    """
    Class contains standard options like generate to csv or generate to file.
    """

    __metaclass__ = abc.ABCMeta

    HEADERS = []
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-d', '--delimiter',
            dest='delimiter',
            default=';',
            help="Delimiter for csv file",
        ),
        make_option(
            '-e', '--encoding',
            dest='encoding',
            default=None,
            help="Output encoding",
        ),
        make_option(
            '-f', '--file_path',
            dest='file_path',
            default=None,
            help="Name of file of generated report",
        ),
    )

    @property
    def help(self):
        return textwrap.dedent(self.__doc__).strip()

    @abc.abstractmethod
    def get_data(self, *args, **options):
        """
        Abstract Method for collects and prepare data

        :return list results: list of lists, nested list represents single row
        """

    def get_prepared_data(self, *args, **options):
        """
        Prepare data for print on screen or send to client. For example
        encoding each cell.

        :return list results: list of lists, nested list represents single row
        """
        data = self.get_data(*args, **options)
        return [self.HEADERS] + map(lambda x: map(unicode, x), data)

    def handle(self, *args, **options):
        """
        Main method, use methods for colleting data and send results on screen

        :param string delimiter: Delimiter for csv format
        """
        # apply default encoding depending on output type
        if not options.get('encoding'):
            if options['file_path']:
                options['encoding'] = DEFAULT_CSV_ENCODING
            else:
                options['encoding'] = DEFAULT_ENCODING

        if options['file_path']:
            writer = UnicodeWriter(
                open(options['file_path'], 'w'),
                delimiter=str(options['delimiter']),
                encoding=options['encoding'],
            )
        else:
            writer = UnicodeWriter(
                self.stdout,
                delimiter=str(options['delimiter']),
                encoding=options['encoding'],
            )
        writer.writerows(self.get_prepared_data(*args, **options))
