# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from ralph_scrooge.models import ServiceEnvironment
from ralph_scrooge.plugins import plugin_runner as plugin_runner
from ralph_scrooge.report.base_plugin_report import BasePluginReport
from ralph_scrooge.utils.common import memoize, AttributeDict


logger = logging.getLogger(__name__)


class ServicesCostsReport(BasePluginReport):
    """
    Reports for services
    """
    cache_section = 'services-costs-report'

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
        extra_cost_plugins = cls._get_extra_cost_plugins()
        dynamic_extra_cost_plugins = cls._get_dynamic_extra_cost_plugins()
        teams_plugins = cls._get_teams_plugins()
        base_usage_types_plugins = cls._get_base_usage_types_plugins()
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins()
        services_plugins = cls._get_pricing_services_plugins()

        plugins = (base_plugins + base_usage_types_plugins +
                   regular_usage_types_plugins + services_plugins +
                   teams_plugins + extra_cost_plugins +
                   dynamic_extra_cost_plugins)

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
        data = defaultdict(dict)
        all_plugins = cls.get_plugins()
        information_plugin, plugins = all_plugins[0], all_plugins[1:]
        progress = 0
        step = 100 / len(plugins)

        def _run_plugin(plugin):
            try:
                logger.info('Calling plugin {} with base usage {}'.format(
                    plugin.plugin_name,
                    plugin.get('plugin_kwargs', {}).get('base_usage', '-'),
                ))
                plugin_report = plugin_runner.run_plugin(
                    'scrooge_reports',
                    plugin.plugin_name,
                    start=start,
                    end=end,
                    forecast=forecast,
                    type='costs',
                    **plugin.get('plugin_kwargs', {})
                )
                for service_id, service_usage in plugin_report.iteritems():
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

        for i, plugin in enumerate(plugins):
            _run_plugin(plugin)
            progress += step
            yield False, progress, {}

        # run information plugin at the end to fetch information only for
        # services with some costs
        information_plugin.plugin_kwargs = {
            'service_environments': ServiceEnvironment.objects.filter(
                pk__in=data.keys()
            )
        }
        _run_plugin(information_plugin)

        yield True, 100, data

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
        for finished, progress, data in cls._get_report_data(
            start,
            end,
            is_active,
            forecast,
            services_environments,
        ):
            if finished:
                yield True, progress, cls._prepare_final_report(
                    data,
                    services_environments
                )
            else:
                yield False, progress, []
