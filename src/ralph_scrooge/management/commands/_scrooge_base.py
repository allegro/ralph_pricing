# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
import textwrap
import sys

from django.core.management.base import BaseCommand

from ralph_scrooge.csvutil import UnicodeWriter


logger = logging.getLogger(__name__)

DEFAULT_ENCODING = 'utf-8'
DEFAULT_CSV_ENCODING = 'cp1250'
DEFAULT_DELIMITER = ';'


class ScroogeBaseCommand(BaseCommand):
    """
    Class contains standard options like generate to csv or generate to file.
    """

    __metaclass__ = abc.ABCMeta

    HEADERS = []
    requires_model_validation = True

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--delimiter',
            dest='delimiter',
            default=DEFAULT_DELIMITER,
            help="Delimiter for csv file",
        )
        parser.add_argument(
            '-e', '--encoding',
            dest='encoding',
            default=None,
            help="Output encoding",
        )
        parser.add_argument(
            '-f', '--file_path',
            dest='file_path',
            default=None,
            help="Name of file of generated report",
        )
        # New options because Django 1.5 has not 'stdout' parameter in
        # call_command function.
        # used in ralph_scrooge/tests/management/commands/test_scrooge_base.py
        parser.add_argument(
            '-s', '--stdout',
            dest='stdout',
            default=None,
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
        self.stdout = options.get('stdout') or sys.stdout
        # apply default encoding depending on output type
        if not options.get('encoding'):
            if options.get('file_path'):
                options['encoding'] = DEFAULT_CSV_ENCODING
            else:
                options['encoding'] = DEFAULT_ENCODING

        if options.get('file_path'):
            writer = UnicodeWriter(
                open(options['file_path'], 'w'),
                delimiter=str(options.get('delimiter', DEFAULT_DELIMITER)),
                encoding=options.get('encoding'),
            )
        else:
            writer = UnicodeWriter(
                self.stdout,
                delimiter=str(options.get('delimiter', DEFAULT_DELIMITER)),
                encoding=options.get('encoding'),
            )
        writer.writerows(self.get_prepared_data(*args, **options))
