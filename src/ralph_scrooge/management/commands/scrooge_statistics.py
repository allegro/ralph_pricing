# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import math
import textwrap
from datetime import datetime, date, timedelta
from optparse import make_option

from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand

from ralph_scrooge.models import UsageType, DailyUsage


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
            '-c',
            dest='only_compare',
            action='store_true',
            default=False,
            help="Show compare date statistics",
        ),
        make_option(
            '--base',
            dest='base',
            default=None,
            help="Base date to compare",
        ),
        make_option(
            '--compare',
            dest='compare',
            default=None,
            help="Date to compare",
        ),
    )

    def _draw_statistics(self, statistics, flags, base_date, compare_date):
        '''
        Draw statistics data on screen in user friendly format

        :param dict statistics: dict with generated statistics data
        :param dict flags: dict with flags
        :param datetime base_date: first (higher) date
        :param datetime compare_date: compare (lower) date
        '''
        def draw(data, name, date):
            def draw_lines(x):
                return '-' * x
            logger.info(
                '{0}[{1} ({2})]{3}'.format(
                    draw_lines(20),
                    name,
                    date,
                    draw_lines(20),
                )
            )
            for key, value in data.iteritems():
                logger.info('{0:>50} | {1:<10}'.format(key, value))

        if flags.get('only_base', False) or flags.get('show_all', False):
            draw(statistics['base'], 'Base', base_date)
        if flags.get('only_compare', False) or flags.get('show_all', False):
            draw(statistics['compare'], 'Second', compare_date)
        if flags.get('only_warnings', False) or flags.get('show_all', False):
            draw(
                statistics['warnings'],
                'Warnings',
                '{0} - {1}'.format(base_date, compare_date),
            )
        if flags.get('only_errors', False) or flags.get('show_all', False):
            draw(
                statistics['errors'],
                'Errors',
                '{0} - {1}'.format(base_date, compare_date),
            )

    def handle(self, base, compare, *args, **options):
        '''
        Generate/rebuild dates, generate flags and data dicts and print it
        on screen

        :param datetime base_date: first (higher) date
        :param datetime compare_date: compare (lower) date
        '''
        def to_date(date):
            return datetime.strptime(date, '%Y-%m-%d').date()

        base = to_date(base) if base else date.today() - timedelta(days=1)
        compare = to_date(compare) if compare else base - timedelta(days=1)

        flags = ['only_errors', 'only_warnings', 'only_base', 'only_compare']
        flag_settings = {'show_all': True}
        for flag_name in flags:
            flag_settings[flag_name] = options.get(flag_name)
            if flag_settings[flag_name]:
                flag_settings['show_all'] = False

        self._draw_statistics(
            self.compare_days(base, compare),
            flag_settings,
            base,
            compare,
        )

    def get_standard_usages_count(self, date, usage):
        """
        Get usages count for given date and usage type

        :param datetime date: Date for whitch data will be selected
        :param object usage: Usage tof whitch data will be selected
        :returns int: Count of total usages
        :rtype int:
        """
        return DailyUsage.objects.filter(
            date__lt=date + timedelta(days=1),
            date__gte=date,
            type=usage,
        ).count()

    def get_statistics(self, date):
        """
        Get data for given date and progress it to UsageName:Count format

        :param datetime compare_date: Date for whitch data will be select
        :returns dict: Dict where key is usage type name and value is total
        usages count
        :rtype dict:
        """

        results = OrderedDict()
        for usage in UsageType.objects.order_by('name'):
            func = getattr(
                self,
                "get_{0}_usages_count".format(usage.name),
                self.get_standard_usages_count,
            )
            results[usage.name] = func(date, usage)
        return results

    def compare_data(self, base_data, compare_data):
        '''
        Compare two dict with data. Return differences betwen given data.

        :param dict base_data: Statistics data for base date
        :param dict compare_data: Statistics data for compare date
        :returns dict: Dict with differences betwen given data
        :rtype dict:
        '''
        results = OrderedDict()
        for key, value in base_data.iteritems():
            results[key] = int(value) - int(compare_data.get(key, 0))
        return results

    def get_warnings(self, base_data, differences_data, percent):
        '''
        Try to find any warnings. If data stroke are more then given percent
        this should be marks as warning

        :param dict base_data: Statistics data for base date
        :param dict differences_data: Differences data
        :param int percent: Percent for defining the warning limits
        :returns dict: Usage types whitch can be errors
        :rtype dict:
        '''
        results = OrderedDict()
        for key, value in base_data.iteritems():
            differences_value = math.fabs(differences_data.get(key, 0))
            if (value * percent / 100) < differences_value:
                results[key] = differences_data.get(key, 0)
        return results

    def get_errors(self, base_data, differences_data):
        '''
        Try to find any errors. If data from compare_date are not null but
        data from base_date are then we have error.

        :param dict base_data: Statistics data for base date
        :param dict differences_data: Differences data
        :returns dict: Error usage types
        :rtype dict:
        '''
        results = OrderedDict()
        for key, value in base_data.iteritems():
            if value == 0 and differences_data.get(key, 0) != 0:
                results[key] = differences_data[key]
        return results

    def compare_days(self, base_date, compare_date):
        '''
        Compare data from two given dates and try find errors or warnings

        :param datetime base_date: first (higher) date
        :param datetime compare_date: compare (lower) date
        :param int percent: Percent for defining the warning limits
        :returns dict: Statistics data
        :rtype dict:
        '''
        results = {
            'base': self.get_statistics(base_date),
            'compare': self.get_statistics(compare_date),
        }
        results['differences'] = self.compare_data(
            results['base'],
            results['compare'],
        )
        results['warnings'] = self.get_warnings(
            results['base'],
            results['differences'],
            settings.WARNINGS_LIMIT_FOR_USAGES,
        )
        results['errors'] = self.get_errors(
            results['base'],
            results['differences'],
        )
        return results
