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
    UsageType,
    Venture,
)
from ralph_pricing.forms import DateRangeForm
from ralph.util import plugin
from ralph_pricing.plugins import reports  # noqa


logger = logging.getLogger(__name__)


class AllVenturesBeta(Report):
    """
    Reports for all ventures
    """
    template_name = 'ralph_pricing/ventures_all.html'
    Form = DateRangeForm
    section = 'all-ventures'
    report_name = _('All Ventures Report Beta')
    currency = 'PLN'

    @classmethod
    def _get_usage_types(cls):
        """
        Returns usage types which should be visible on report
        """
        logger.debug("Getting usage types")
        return UsageType.objects.exclude(
            show_in_report=False,
        ).exclude(show_in_report=False).order_by('-order', 'name')

    @classmethod
    def _get_as_currency(cls, field_content, total_cost):
        """
        Change field content to currency format. Returned format looks like
        <field_content as two decimal value> <currency>

        :param decimal field_content: Value to reformat
        :param boolean total_cost: Information about return value as total
        cost or D(0)
        :returns tuple: Reformated field content and value for total cost
        :rtype tuple:
        """
        field_content = D(field_content)

        currency_field = '{0:.2f} {1}'.format(
            field_content,
            cls.currency,
        )

        return currency_field, field_content if total_cost else D(0)

    @classmethod
    def _prepare_field(cls, field_name, field_rules, venture_data):
        """
        Prepare single field for one row for single column. For example,
        here is a place for format filed as currency or set default value

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

        if isinstance(field_content, str):
            return field_content, usage_cost

        if 'currency' in field_rules and field_rules['currency']:
            field_content, usage_cost = cls._get_as_currency(
                field_content,
                field_rules.get('total_cost', False),
            )

        return field_content, usage_cost

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
        venture_row.append('{0:.2f} {1}'.format(total_cost, cls.currency))
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
    def _get_ventures(cls, show_in_ralph):
        """
        This function return all ventures for which report will be ganarated

        :param boolean show_in_ralph: Flag. Get only active or all.
        :returns list: list of ventures
        :rtype list:
        """
        logger.debug("Getting ventures")
        ventures = Venture.objects.order_by('name')
        if show_in_ralph:
            ventures = ventures.filter(is_active=True)
        logger.debug("Got {0} ventures".format(ventures.count()))
        return ventures

    @classmethod
    def _get_report_data(cls, start, end, show_in_ralph, forecast, ventures):
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
        data = {venture.id: {} for venture in ventures}
        for i, usage_type in enumerate(cls._get_usage_types()):
            try:
                usage_type_report = plugin.run(
                    'reports',
                    '{0}_usages'.format(usage_type.symbol),
                    ventures=ventures,
                    start=start,
                    end=end,
                    forecast=forecast,
                )
                for venture_id, venture_usage in usage_type_report.iteritems():
                    if venture_id in data:
                        data[venture_id].update(venture_usage)
            except KeyError:
                logger.warning(
                    "Usage '{0}' have no usage plugin".format(usage_type.name)
                )

        return data

    @classmethod
    def get_data(
        cls,
        start,
        end,
        show_in_ralph=False,
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
        ventures = cls._get_ventures(show_in_ralph)
        data = cls._get_report_data(
            start,
            end,
            show_in_ralph,
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
        for usage_type in cls._get_usage_types():
            try:
                usage_type_headers = plugin.run(
                    'reports',
                    '{0}_schema'.format(usage_type.symbol),
                    warehouse='1',
                )
                header.append(usage_type_headers)
            except KeyError:
                logger.warning(
                    "Usage '{0}' have no schema plugin".format(usage_type.name)
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
                header.append(value['name'])
        header.append(_("Total cost"))
        return header
