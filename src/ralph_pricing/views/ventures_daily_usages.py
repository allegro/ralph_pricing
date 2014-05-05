# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from dateutil import rrule

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report
from ralph_pricing.models import (
    UsageType,
    Venture,
)
from ralph_pricing.forms import VenturesDailyUsagesForm
from ralph.util import plugin as plugin_runner
from ralph_pricing.plugins import reports  # noqa


logger = logging.getLogger(__name__)


class VenturesDailyUsages(Report):
    """
    Reports for ventures dailyusages
    """
    template_name = 'ralph_pricing/ventures_daily_usages.html'
    Form = VenturesDailyUsagesForm
    section = 'ventures-daily-usages'
    report_name = _('Ventures Daily Usages Report')

    @property
    def initial(self):
        """
        Initially selected values for usage types on form.
        """
        usage_types = UsageType.objects.filter(symbol__in=[
            'deprecation',
            'physical_cpu_cores'
        ])
        return {'usage_types': [u.id for u in usage_types]}

    @classmethod
    def _get_ventures(cls, is_active):
        """
        Returns all ventures for which report will be ganerated.

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
    def _prepare_final_report(cls, start, end, usage_types, data, ventures):
        """
        Convert information from dict to list. In this case data must be
        understandable for generating reports in html. Data format is:

        data = {
            day: {
                usage_type1_symbol: {
                    venture1_id: value1,
                    venture2_id: value2,
                },
                usage_type2_symbol: {
                    venture1_id: value1,
                    venture2_id: value2,
                },
                ...
            },
            ...
        }

        As a result method should return list of lists where each sublist is
        row with usages for specified venture (0 when there are no usages of
        usage type).

        :param dict data: Complete report data for ventures daily usages.
        :returns list: prepared data to generating report in html
        :rtype list:
        """
        logger.debug("Preparing final report")
        final_data = []
        for venture in ventures:
            # venture ancestors path
            venture_name = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )
            venture_data = [venture_name]
            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                date = day.date()
                for usage_type in usage_types:
                    try:
                        value = data[date][usage_type.symbol][venture.id]
                    except KeyError:
                        value = 0
                    venture_data.append(value)
            final_data.append(venture_data)
        return final_data

    @classmethod
    def _get_report_data(cls, start, end, usage_types, ventures):
        """
        Use plugins to get daily usages data for given ventures. Plugin return
        value format:

        data_from_plugin = {
            'day': {
                'venture_id': value,
                'venture_id2': value2,
            },
            ...
        }

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param list usage_types: Usage types to use
        :param list ventures: List of ventures for which data must be taken
        :returns dict: Complete report data for ventures daily usages
        :rtype dict:
        """
        logger.debug("Getting ventures dailyusages report data")
        data = {day.date(): {} for day in rrule.rrule(
            rrule.DAILY,
            dtstart=start,
            until=end
        )}
        for usage_type in usage_types:
            plugin_name = usage_type.get_plugin_name()
            try:
                plugin_report = plugin_runner.run(
                    'reports',
                    plugin_name,
                    ventures=ventures,
                    start=start,
                    end=end,
                    usage_type=usage_type,
                    type='dailyusages',
                )
                for day, day_usages in plugin_report.iteritems():
                    data[day][usage_type.symbol] = day_usages
            except KeyError:
                logger.warning(
                    "Usage '{0}' has no usage plugin".format(plugin_name)
                )
            except BaseException as e:
                logger.error("Report generate error: {0}".format(e))
        return data

    @classmethod
    def get_data(
        cls,
        start,
        end,
        usage_types,
        is_active=False,
        **kwargs
    ):
        """
        Main method. Create a full report for daily usages by ventures.
        Process of creating report consists of two parts. First of them is
        collecting all required data. Second step is preparing data to render
        in html.

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info(
            "Generating venture dailyusages report from {0} to {1}".format(
                start,
                end,
            )
        )
        ventures = cls._get_ventures(is_active)
        data = cls._get_report_data(
            start,
            end,
            usage_types,
            ventures,
        )
        yield 100, cls._prepare_final_report(
            start,
            end,
            usage_types,
            data,
            ventures,
        )

    @classmethod
    def get_header(cls, start, end, usage_types, **kwargs):
        """
        Return all headers for daily usages report.

        :returns list: Complete collection of headers for report
        :rtype list:
        """
        logger.debug("Getting headers for report")
        header = [
            [
                (_('Venture'), {'rowspan': 2})
            ],
            [],
        ]
        usage_types_headers = []
        for usage_type in usage_types:
            usage_type_header = plugin_runner.run(
                'reports',
                usage_type.get_plugin_name(),
                usage_type=usage_type,
                type='dailyusages_header',
            )
            usage_types_headers.append(usage_type_header)

        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            header[0].append((day.date(), {'colspan': len(usage_types)}))
            header[1].extend(usage_types_headers)
        return header
