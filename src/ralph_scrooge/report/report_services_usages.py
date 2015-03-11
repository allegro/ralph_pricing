# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from dateutil import rrule
from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin as plugin_runner
from ralph_scrooge.report.base_plugin_report import BasePluginReport


logger = logging.getLogger(__name__)


class ServicesUsagesReport(BasePluginReport):
    """
    Report with usages of resources (usage types) by service environments
    per days
    """
    cache_section = 'services-usages-report'

    @classmethod
    def _prepare_field(cls, value, usage_type):
        """
        Prepare single field for one row for single column. For example,
        here is a place for format field as currency or set default value.
        """
        if not isinstance(value, (int, D, float, long)):
            return value

        if usage_type.divide_by:
            value = value / float(10 ** usage_type.divide_by)

        value = '{:.{prec}f}'.format(value, prec=usage_type.rounding)
        return value

    @classmethod
    def _prepare_final_report(
        cls,
        start,
        end,
        usage_types,
        data,
        service_environments
    ):
        """
        Convert information from dict to list. In this case data must be
        understandable for generating reports in html. Data format is:

        data = {
            day: {
                usage_type1_id: {
                    service_environment_1_id: value1,
                    service_environment_2_id: value2,
                },
                usage_type2_id: {
                    service_environment_1_id: value1,
                    service_environment_2_id: value2,
                },
                ...
            },
            ...
        }

        As a result method should return list of lists where each sublist is
        row with usages for specified service environment (0 when there are
        no usages of usage type).

        :param dict data: Complete report data for service environments daily
        usages.
        :returns list: prepared data to generating report in html
        :rtype list:
        """
        logger.debug("Preparing final report")
        final_data = []
        for se in service_environments:
            # TODO: add historical information (name between start and end)
            se_data = [se.service.name, se.environment.name]
            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                date = day.date()
                for usage_type in usage_types:
                    try:
                        value = cls._prepare_field(
                            data[date][usage_type.id][se.id],
                            usage_type
                        )
                    except KeyError:
                        value = cls._prepare_field(
                            0,
                            usage_type
                        )
                    se_data.append(value)
            final_data.append(se_data)
        return final_data

    @classmethod
    def _get_report_data(cls, start, end, usage_types, service_environments):
        """
        Use plugins to get daily usages data for given service environments.
        Plugin should return data in following format:

        data_from_plugin = {
            'day': {
                'service_environment_1_id': value,
                'service_environment_2_id': value2,
            },
            ...
        }

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param list usage_types: Usage types to use
        :param list service_environments: List of service environments for
            which data must be taken
        :returns dict: Complete report data for service environments daily
            usages
        :rtype dict:
        """
        logger.debug("Getting services environments dailyusages report data")
        data = {day.date(): {} for day in rrule.rrule(
            rrule.DAILY,
            dtstart=start,
            until=end
        )}
        for usage_type in usage_types:
            plugin_name = usage_type.get_plugin_name()
            try:
                plugin_report = plugin_runner.run(
                    'scrooge_reports',
                    plugin_name,
                    type='usages',
                    start=start,
                    end=end,
                    usage_type=usage_type,
                    service_environments=service_environments,
                )
                for day, day_usages in plugin_report.iteritems():
                    data[day][usage_type.id] = day_usages
            except KeyError:
                logger.warning(
                    "Usage '{0}' has no usage plugin".format(plugin_name)
                )
            except Exception as e:
                logger.exception(
                    "Error while generating the report: {0}".format(e)
                )
                raise
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
        Main method. Create a full report for daily usages by service
        environments. Process of creating report consists of two parts. First
        of them is collecting all required data. Second step is preparing data
        to render in html.

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info((
            "Generating service environments dailyusages report from {0} "
            "to {1}"
            ).format(
                start,
                end,
            )
        )
        service_environments = cls._get_services_environments(is_active)
        data = cls._get_report_data(
            start,
            end,
            usage_types,
            service_environments,
        )
        yield 100, cls._prepare_final_report(
            start,
            end,
            usage_types,
            data,
            service_environments
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
                (_('Service'), {'rowspan': 2}),
                (_('Environment'), {'rowspan': 2}),
            ],
            [],
        ]
        usage_types_headers = []
        for usage_type in usage_types:
            usage_type_header = plugin_runner.run(
                'scrooge_reports',
                usage_type.get_plugin_name(),
                usage_type=usage_type,
                type='usages_schema',
            )
            usage_types_headers.append(usage_type_header)

        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            header[0].append((day.date(), {'colspan': len(usage_types)}))
            header[1].extend(usage_types_headers)
        return header
