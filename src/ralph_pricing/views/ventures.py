# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from decimal import Decimal as D

from lck.cache import memoize
from django.conf import settings
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report
from ralph_pricing.models import (
    Service,
    UsageType,
    Venture,
)
from ralph_pricing.forms import DateRangeForm
from ralph.util import plugin as plugin_runner
from ralph_pricing.plugins import reports  # noqa
from ralph_pricing.plugins.reports.base import AttributeDict


logger = logging.getLogger(__name__)


class AllVentures(Report):
    """
    Reports for all ventures
    """
    template_name = 'ralph_pricing/ventures_all.html'
    Form = DateRangeForm
    section = 'all-ventures'
    report_name = _('All Ventures Report')
    currency = 'PLN'

    @classmethod
    def _get_base_usage_types(cls):
        """
        Returns base usage types which should be visible on report
        """
        logger.debug("Getting usage types")
        return UsageType.objects.filter(
            show_in_report=True,
            type='BU',
        ).order_by('-order', 'name')

    @classmethod
    def _get_regular_usage_types(cls):
        """
        Returns regular usage types which should be visible on report
        """
        return UsageType.objects.filter(
            show_in_report=True,
            type='RU',
        ).order_by('-order', 'name')

    @classmethod
    def _get_services(cls):
        """
        Returns services which should be visible on report
        """
        return Service.objects.order_by('name')

    @classmethod
    def _get_base_usage_types_plugins(cls):
        """
        Returns plugins information (name and arguments) for base usage types
        """
        base_usage_types = cls._get_base_usage_types()
        result = []
        for but in base_usage_types:
            but_info = AttributeDict(
                name=but.name,
                plugin_name=but.get_plugin_name(),
                plugin_kwargs={
                    'usage_type': but,
                    'no_price_msg': True,
                }
            )
            result.append(but_info)
        return result

    @classmethod
    def _get_regular_usage_types_plugins(cls):
        """
        Returns plugins information (name and arguments) for regular usage
        types
        """
        regular_usage_types = cls._get_regular_usage_types()
        result = []
        for rut in regular_usage_types:
            rut_info = AttributeDict(
                name=rut.name,
                plugin_name=rut.get_plugin_name(),
                plugin_kwargs={
                    'usage_type': rut,
                    'no_price_msg': True,
                }
            )
            result.append(rut_info)
        return result

    @classmethod
    def _get_services_plugins(cls):
        """
        Returns plugins information (name and arguments) for services
        """
        services = cls._get_services()
        result = []
        for service in services:
            service_info = AttributeDict(
                name=service.name,
                plugin_name=service.get_plugin_name(),
                plugin_kwargs={
                    'service': service
                }
            )
            result.append(service_info)
        return result

    @classmethod
    @memoize
    def _get_plugins(cls):
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
    def _prepare_field(cls, field_name, field_rules, venture_data):
        """
        Prepare single field for one row for single column. For example,
        here is a place for format field as currency or set default value

        :param string field_name: Key for define which value must be taken
        :param dict field_rules: Schema for this field
        :param dict venture_data: Dict which contains data for one row
        :returns tuple: prepared field content and price to include in the
        total cost of
        :rtype tuple:
        """
        field_content = venture_data.get(
            field_name,
            field_rules['default'] if 'default' in field_rules else 0.0,
        )
        usage_cost = D(0)

        if not isinstance(field_content, (int, D, float, long)):
            return field_content, usage_cost

        if 'total_cost' in field_rules and field_rules['total_cost']:
            usage_cost = D(field_content)

        if 'currency' in field_rules and field_rules['currency']:
            field_content = '{0:.2f}'.format(field_content)

        return field_content,  usage_cost

    @classmethod
    def _prepare_venture_row(cls, venture_data):
        """
        Prepare one row for single venture. Return list of lists agreed with
        all columns.

        :param dict venture_data: Dict which contains data for one row
        :returns list: List of lists with data for each column
        :rtype list:
        """
        venture_row = []
        total_cost = D(0)
        for schema in cls._get_schema():
            plugin_fields = []
            for field_name, field_rules in schema.iteritems():
                field_content, usage_cost = cls._prepare_field(
                    field_name,
                    field_rules,
                    venture_data,
                )
                plugin_fields.append(field_content)
                total_cost += usage_cost
            venture_row.extend(plugin_fields)
        venture_row.append('{0:.2f}'.format(total_cost))
        return venture_row

    @classmethod
    def _prepare_final_report(cls, data, ventures):
        """
        Convert information from dict to list. In this case data must be
        understandable for generating reports in html. Data returned by
        plugins are in format:

        data = {
            'venture_id': {
                'field1_name': value,
                'field2_name': value,
                ...
            }
        }

        but html report except data like:

        returned_data = [[value, value], [value, value]]

        so, we need convert data from first example to second one

        :param dict data: Complete report data for all ventures.
        :returns list: prepared data to generating report in html
        :rtype list:
        """
        logger.debug("Preparing final report")
        final_data = []
        for venture in ventures:
            final_data.append(
                cls._prepare_venture_row(data.get(venture.id, {}))
            )
        return final_data

    @classmethod
    def _get_ventures(cls, is_active):
        """
        This function return all ventures for which report will be ganarated

        :param boolean is_active: Flag. Get only active or all.
        :returns list: list of ventures
        :rtype list:
        """
        logger.debug("Getting ventures")
        ventures = Venture.objects.order_by('name')
        if is_active:
            ventures = ventures.filter(is_active=True)
        logger.debug("Got {0} ventures".format(ventures.count()))
        return ventures

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
        for i, plugin in enumerate(cls._get_plugins()):
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
            except BaseException as e:
                logger.exception("Report generate error: {0}".format(e))
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

    @classmethod
    @memoize
    def _get_schema(cls):
        """
        Use plugins to get full schema for report

        :returns dict: Complete schema for all columns in report
        :rtype dict:
        """
        logger.debug("Getting schema for report")
        header = []
        for plugin in cls._get_plugins():
            try:
                plugin_headers = plugin_runner.run(
                    'reports',
                    plugin.plugin_name,
                    type='schema',
                    **plugin.get('plugin_kwargs', {})
                )
                header.append(plugin_headers)
            except KeyError:
                logger.warning(
                    "Usage '{0}' has no schema plugin".format(plugin.name)
                )
        return header

    @classmethod
    def get_header(cls, **kwargs):
        """
        Return all headers for report

        :returns list: Complete collection of headers for report
        :rtype list:
        """
        logger.debug("Getting headers for report")
        header = []
        for schema in cls._get_schema():
            for key, value in schema.iteritems():
                if 'currency' in value and value['currency']:
                    value['name'] = "{0} - {1}".format(
                        value['name'],
                        cls.currency,
                    )
                header.append(value['name'])
        header.append(_("Total cost"))
        return [header]
