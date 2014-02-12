# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import defaultdict
from decimal import Decimal as D
from lck.cache import memoize

from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Count

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
    ExtraCost,
    ExtraCostType,
    UsageType,
    Venture,
)
from ralph_pricing.forms import DateRangeForm
from ralph.util import plugin
from ralph_pricing.plugins import reports


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
        return UsageType.objects.exclude(
            is_plug=False,
        ).exclude(show_in_report=False).order_by('-order', 'name')

    @classmethod
    def _get_as_currency(cls, field_content, total_cost):
        field_content = D(field_content)

        currency_field = '{0:.2f} {1}'.format(
            field_content,
            cls.currency,
        )

        return currency_field, field_content if total_cost else D(0)

    @classmethod
    def _prepare_field(cls, field_name, field_rules, venture_data):
        field_content = venture_data.get(
            field_name,
            field_rules['default'] if 'default' in field_rules else 0.0,
        )
        usage_cost = D(0)

        if type(field_content) == str:
            return field_content, usage_cost

        if 'currency' in field_rules and field_rules['currency']:
            field_content, usage_cost = cls._get_as_currency(
                field_content,
                field_rules.get('total_cost', False),
            )

        return field_content, usage_cost

    @classmethod
    def _prepare_venture_row(cls, venture_data):
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
        final_data = []
        for venture in ventures:
            final_data.append(
                cls._prepare_venture_row(data.get(venture.id, {}))
            )
        return final_data

    @classmethod
    def _get_ventures(cls, show_in_ralph):
        ventures = Venture.objects.order_by('name')
        if show_in_ralph:
            ventures = ventures.filter(is_active=True)
        return ventures

    @classmethod
    def _get_report_data(cls, start, end, show_in_ralph, forecast, ventures):
        data = {venture.id: {} for venture in ventures}
        for i, usage_type in enumerate(cls._get_usage_types()):
            usage_type_report = plugin.run(
                'usages',
                '{0}_usages'.format(usage_type.name),
                ventures=ventures,
                start=start,
                end=end,
                show_in_ralph=show_in_ralph,
                forecast=forecast,
            )
            for venture_id, venture_usage in usage_type_report.iteritems():
                if venture_id in data:
                    data[venture_id].update(venture_usage)
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
        header = []
        for usage_type in cls._get_usage_types():
            usage_type_headers = plugin.run(
                'usages',
                '{0}_schema'.format(usage_type.name),
                warehouse='1',
            )
            header.append(usage_type_headers)
        return header

    @classmethod
    def get_header(cls, **kwargs):
        logger.debug("Getting schema for report")
        header = []
        for schema in cls._get_schema():
            for key, value in schema.iteritems():
                header.append(value['name'])
        header.append(_("Total cost"))
        return header
