# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import textwrap
from datetime import datetime, date, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand

from ralph_pricing.models import DailyStatistics


logger = logging.getLogger(__name__)


class PluginError(Exception):
    pass


class Command(BaseCommand):
    """Retrieve data for pricing for base"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-e',
            dest='only_errors',
            action='store_true',
            default=False,
            help="Show errors",
        ),
        make_option(
            '-w',
            dest='only_warnings',
            action='store_true',
            default=False,
            help="Show warnings",
        ),
        make_option(
            '-b',
            dest='only_base',
            action='store_true',
            default=False,
            help="Show base date statistics",
        ),
        make_option(
            '-s',
            dest='only_second',
            action='store_true',
            default=False,
            help="Show second date statistics",
        ),
        make_option(
            '--base',
            dest='base',
            default=None,
            help="Base date to second",
        ),
        make_option(
            '--second',
            dest='second',
            default=None,
            help="Date to second",
        ),
    )

    def _draw_statistics(self, statistics, flags, base_date, second_date):
        '''
        Draw statistics data on screen in user friendly format

        :param dict statistics: dict with generated statistics data
        :param dict flags: dict with flags
        :param datetime base_date: first (higher) date
        :param datetime second_date: second (lower) date
        '''
        def draw(data, name, date):
            draw_lines = lambda x: ''.join(['-' for y in xrange(x)])
            print (
                '{0}[{1} ({2})]{3}'.format(
                    draw_lines(50),
                    name,
                    date,
                    draw_lines(50),
                )
            )
            for key, value in data.iteritems():
                print ('{0:>50} | {1:<10}'.format(key, value))

        if flags.get('only_base', False) or flags.get('show_all', False):
            draw(statistics['base'], 'Base', base_date)
        if flags.get('only_second', False) or flags.get('show_all', False):
            draw(statistics['second'], 'Second', second_date)
        if flags.get('only_warnings', False) or flags.get('show_all', False):
            draw(
                statistics['warnings'],
                'Warnings',
                '{0} - {1}'.format(base_date, second_date),
            )
        if flags.get('only_errors', False) or flags.get('show_all', False):
            draw(
                statistics['errors'],
                'Errors',
                '{0} - {1}'.format(base_date, second_date),
            )

    def handle(self, base, second, *args, **options):
        '''
        Generate/rebuild dates, generate flags and data dicts and print it
        on screen

        :param datetime base_date: first (higher) date
        :param datetime second_date: second (lower) date
        '''
        to_date = lambda date: datetime.strptime(date, '%Y-%m-%d').date()
        base = to_date(base) if base else date.today()
        second = to_date(second) if second else base - timedelta(days=1)

        flags = ['only_errors', 'only_warnings', 'only_base', 'only_second']
        flag_settings = {'show_all': True}
        for flag_name in flags:
            flag_settings[flag_name] = options.get(flag_name)
            if flag_settings[flag_name]:
                flag_settings['show_all'] = False

        self._draw_statistics(
            DailyStatistics.compare_days(base, second),
            flag_settings,
            base,
            second,
        )
