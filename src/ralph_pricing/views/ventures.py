# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from lck.cache import memoize
from django.conf import settings
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.base_plugin_report import BasePluginReport
from ralph_pricing.forms import VenturesReportForm
from ralph.util import plugin as plugin_runner
from ralph_pricing.plugins import reports  # noqa
from ralph_pricing.plugins.reports.base import AttributeDict


logger = logging.getLogger(__name__)


class AllVentures(BasePluginReport):
    """
    Reports for all ventures
    """
    template_name = 'ralph_pricing/ventures_all.html'
    Form = VenturesReportForm
    section = 'all-ventures'
    report_name = _('All Ventures Report')

    @classmethod
    @memoize
    def get_plugins(cls):
        """
        Returns list of plugins to call, with information and extra cost about
        each, such as name and arguments
        """
        base_plugins = [
            AttributeDict(name='Information', plugin_name='information'),
        ]
        extra_cost_plugins = [
            AttributeDict(
                name='ExtraCostsPlugin',
                plugin_name='extra_cost_plugin',
            ),
        ]
        base_usage_types_plugins = cls._get_base_usage_types_plugins()
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins()
        services_plugins = cls._get_services_plugins()
        plugins = (base_plugins + base_usage_types_plugins +
                   regular_usage_types_plugins + services_plugins +
                   extra_cost_plugins)
        return plugins

    @classmethod
    def _get_report_data(cls, start, end, is_active, forecast, ventures):
        """
        Use plugins to get usages data for given ventures. Plugin logic can be
        so complicated but for this method, plugin must return value in
        format:

        data_from_plugin = {
            'venture_id': {
                'field1_name': value,
                'field2_name': value,
                ...
            },
            ...
        }

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param boolean forecast: Forecast prices or real
        :param list ventures: List of ventures for which data must be taken
        :returns dict: Complete report data for all ventures
        :rtype dict:
        """
        logger.debug("Getting report date")
        old_queries_count = len(connection.queries)
        data = {venture.id: {} for venture in ventures}
        for i, plugin in enumerate(cls.get_plugins()):
            try:
                plugin_old_queries_count = len(connection.queries)
                plugin_report = plugin_runner.run(
                    'reports',
                    plugin.plugin_name,
                    ventures=ventures,
                    start=start,
                    end=end,
                    forecast=forecast,
                    type='costs',
                    **plugin.get('plugin_kwargs', {})
                )
                for venture_id, venture_usage in plugin_report.iteritems():
                    if venture_id in data:
                        data[venture_id].update(venture_usage)
                plugin_queries_count = (
                    len(connection.queries) - plugin_old_queries_count
                )
                if settings.DEBUG:
                    logger.debug('Plugin SQL queries: {0}\n'.format(
                        plugin_queries_count
                    ))
            except KeyError:
                logger.warning(
                    "Usage '{0}' have no usage plugin".format(plugin.name)
                )
            except Exception as e:
                logger.exception(
                    "Error while generating the report: {0}".format(e)
                )
                raise
        queries_count = len(connection.queries) - old_queries_count
        if settings.DEBUG:
            logger.debug('Total SQL queries: {0}'.format(queries_count))
        return data

    @classmethod
    def get_data(
        cls,
        start,
        end,
        is_active=False,
        forecast=False,
        **kwargs
    ):
        """
        Main method. Create a full report for all ventures. Process of creating
        report consists of two parts. First of them is collect all requirement
        data. Second step is prepare data to render in html

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info("Generating report from {0} to {1}".format(start, end))
        ventures = cls._get_ventures(is_active)
        data = cls._get_report_data(
            start,
            end,
            is_active,
            forecast,
            ventures,
        )
        yield 100, cls._prepare_final_report(data, ventures)
