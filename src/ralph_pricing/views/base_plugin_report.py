# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from decimal import Decimal as D

from lck.cache import memoize
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report
from ralph_pricing.models import (
    Service,
    UsageType,
    Venture,
)
from ralph.util import plugin as plugin_runner
from ralph_pricing.plugins import reports  # noqa
from ralph_pricing.plugins.reports.base import AttributeDict


logger = logging.getLogger(__name__)


class BasePluginReport(Report):
    schema_name = 'schema'

    @classmethod
    def get_plugins(cls):
        """
        Should return list of plugins to call
        """
        return []

    @classmethod
    def _get_base_usage_types(cls, filter_=None):
        """
        Returns base usage types which should be visible on report
        """
        logger.debug("Getting usage types")
        query = UsageType.objects.filter(
            show_in_ventures_report=True,
            type='BU',
        )
        if filter_:
            query = query.filter(**filter_)
        return query.order_by('-order', 'name')

    @classmethod
    def _get_base_usage_types_plugins(cls, filter_=None):
        """
        Returns plugins information (name and arguments) for base usage types
        """
        base_usage_types = cls._get_base_usage_types(filter_)
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
    def _get_regular_usage_types(cls, filter_=None):
        """
        Returns regular usage types which should be visible on report
        """
        query = UsageType.objects.filter(
            show_in_ventures_report=True,
            type='RU',
        )
        if filter_:
            query = query.filter(**filter_)
        return query.order_by('-order', 'name')

    @classmethod
    def _get_regular_usage_types_plugins(cls, filter_=None):
        """
        Returns plugins information (name and arguments) for regular usage
        types
        """
        regular_usage_types = cls._get_regular_usage_types(filter_)
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
    def _get_services(cls):
        """
        Returns services which should be visible on report
        """
        return Service.objects.order_by('name')

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
    def _prepare_field(cls, field_name, field_rules, field_data):
        """
        Prepare single field for one row for single column. For example,
        here is a place for format field as currency or set default value

        :param string field_name: Key for define which value must be taken
        :param dict field_rules: Schema for this field
        :param dict field_data: Dict which contains data for one row
        :returns tuple: prepared field content and price to include in the
        total cost of
        :rtype tuple:
        """
        field_content = field_data.get(
            field_name,
            field_rules['default'] if 'default' in field_rules else 0.0,
        )
        usage_cost = D(0)

        if not isinstance(field_content, (int, D, float, long)):
            return field_content, usage_cost

        if 'total_cost' in field_rules and field_rules['total_cost']:
            usage_cost = D(field_content)

        if field_rules.get('rounding') is not None:
            field_content = round(field_content, field_rules['rounding'])

        if 'currency' in field_rules and field_rules['currency']:
            field_content = '{0:.2f}'.format(field_content)

        return field_content, usage_cost

    @classmethod
    def _prepare_row(cls, data):
        """
        Prepare one row for single venture. Return list of lists agreed with
        all columns.

        :param dict data: Dict which contains data for one row
        :returns list: List of lists with data for each column
        :rtype list:
        """
        row = []
        total_cost = D(0)
        for schema in cls._get_schema():
            plugin_fields = []
            for field_name, field_rules in schema.iteritems():
                field_content, usage_cost = cls._prepare_field(
                    field_name,
                    field_rules,
                    data,
                )
                plugin_fields.append(field_content)
                total_cost += usage_cost
            row.extend(plugin_fields)
        row.append('{0:.2f}'.format(total_cost))
        return row

    @classmethod
    def _prepare_final_report(cls, intial_data, data):
        """
        Convert information from dict to list. In this case data must be
        understandable for generating reports in html. Data returned by
        plugins are in format:

        data = {
            'object_id': {
                'field1_name': value,
                'field2_name': value,
                ...
            }
        }

        but html report except data like:

        returned_data = [[value, value], [value, value]]

        so, we need convert data from first example to second one

        :param dict initial_data: inital_data to fill in.
        :param dict data: complete report data.
        :returns list: prepared data to generating report in html
        :rtype list:
        """
        logger.debug("Preparing final report")
        final_data = []
        for row in data:
            final_data.append(
                cls._prepare_row(intial_data.get(row.id, {}))
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
    @memoize
    def _get_schema(cls):
        """
        Use plugins to get full schema for report

        :returns dict: Complete schema for all columns in report
        :rtype dict:
        """
        logger.debug("Getting schema for report")
        header = []
        for plugin in cls.get_plugins():
            try:
                plugin_headers = plugin_runner.run(
                    'reports',
                    plugin.plugin_name,
                    type=cls.schema_name,
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
