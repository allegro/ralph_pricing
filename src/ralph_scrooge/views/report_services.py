# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import datetime

from ralph_scrooge.utils import memoize
from django.conf import settings
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.views.base_plugin_report import BasePluginReport
from ralph_scrooge.forms import ServicesReportForm
from ralph.util import plugin as plugin_runner
from ralph_scrooge.plugins import reports  # noqa
from ralph_scrooge.utils import AttributeDict
from ralph_scrooge.models import ExtraCostType


logger = logging.getLogger(__name__)


class ServicesReport(BasePluginReport):
    """
    Reports for services
    """
    template_name = 'ralph_scrooge/report_services.html'
    Form = ServicesReportForm
    section = 'report-services'
    report_name = _('Services Report')

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
                plugin_kwargs={
                    'extra_cost_type': extra_cost_type,
                }
            ) for extra_cost_type in ExtraCostType.objects.all()
        ]
        plugins = (base_plugins + extra_cost_plugins)
        '''
        base_usage_types_plugins = cls._get_base_usage_types_plugins()
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins()
        services_plugins = cls._get_pricing_services_plugins()
        teams_plugins = cls._get_teams_plugins()
        plugins = (base_plugins + base_usage_types_plugins +
                   regular_usage_types_plugins + services_plugins +
                   teams_plugins)  # + extra_cost_plugins)
        '''
        return plugins

    @classmethod
    def _get_report_data(
        cls,
        start,
        end,
        is_active,
        forecast,
        service_environments,
    ):
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
        data = {se.id: {} for se in service_environments}
        for i, plugin in enumerate(cls.get_plugins()):
            for days in xrange((end - start).days + 1):
                try:
                    plugin_old_queries_count = len(connection.queries)
                    plugin_report = plugin_runner.run(
                        'scrooge_reports',
                        plugin.plugin_name,
                        service_environments=service_environments,
                        start=start,
                        end=end,
                        forecast=forecast,
                        type='costs',
                        **plugin.get('plugin_kwargs', {})
                    )
                    for service_id, service_usage in plugin_report.iteritems():
                        if service_id in data:
                            data[service_id].update(service_usage)

                except KeyError:
                    logger.warning(
                        "Usage '{0}' has no usage plugin".format(plugin.name)
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
        is_active=False,
        forecast=False,
        **kwargs
    ):
        """
        Main method. Create a full report for services. Process of creating
        report consists of two parts. First of them is collect all requirement
        data. Second step is prepare data to render in html

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info("Generating report from {0} to {1}".format(start, end))
        services_environments = cls._get_services_environments(is_active)
        data = cls._get_report_data(
            start,
            end,
            is_active,
            forecast,
            services_environments,
        )
        yield 100, cls._prepare_final_report(data, services_environments)
