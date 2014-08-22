# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from dateutil import rrule

from django.conf import settings
from django.db import connection
from django.db.transaction import commit_on_success

from ralph.util import plugin as plugin_runner
from ralph_scrooge.utils import memoize, AttributeDict
from ralph_scrooge.models import (
    DailyCost,
    ExtraCostType,
    PricingService,
    ServiceEnvironment,
    Team,
    UsageType,
)
from ralph_scrooge.plugins.cost.base import (
    NoPriceCostError,
    MultiplePriceCostError,
)

logger = logging.getLogger(__name__)


class VerifiedDailyCostsExistsError(Exception):
    pass


class Collector(object):
    """
    Costs collector

    Collects all costs (of usage types, teams, extra costs and pricing
    services) and process them (save in database as tree structure).

    All plugins used by collector should return data in following format:
    {
        <service_environment_id>: [
            {
                'type': <type or type_id>,
                'cost': <cost>,
                '_children': [
                    {
                        'type': <type or type_id>,
                        'cost': <cost>,
                        '_children': [...],
                        **kwargs
                    }
                ],
                **kwargs
            }
        ],
        <service_environment_id>: [...],
        ...
    }

    Notice that:
    * kwargs are additional params, that should match DailyCost fields, ex.
        pricing_object(_id), value etc.
    * _children is optional field, and could be nested infinitely

    Example:
    {
        service_environment1.id: [
            {'type': <BaseUsage 1>, 'costs': 100,},
            {'type': 2, 'costs': 200, 'value': 40, 'pricing_object_id': 33,},
        ],
        service_environment2.id: [
            {
                'type': <BaseUsage 1>,
                'costs': 100,
                '_children': [
                    {'type': <BaseUsage 2>, 'costs': 500,},
                    ...
                ]
            },
    }
    """
    def process_period(self, start, end, **kwargs):
        service_environments = self._get_services_environments()
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            self.process(day, service_environments=service_environments, **kwargs)

    @commit_on_success
    def process(
        self,
        date,
        forecast=False,
        delete_verified=False,
        service_environments=None,
    ):
        """
        Process costs for single date.

        Process parts:
        1) delete previously saved costs (if they were not verified, except
            sitution, where delete_verified=True was passed explicitly)
        2) collect costs from all plugins
        3) save costs in database in tree format
        """
        if service_environments is None:
            service_environments = self._get_services_environments()
        self._delete_daily_costs(date, delete_verified)
        costs = self._collect_costs(date, service_environments, forecast)
        self._save_costs(date, costs, forecast)

    def _delete_daily_costs(self, date, delete_verified=False):
        """
        Check if there are any verfifed daily costs for given date.
        If no, delete previously saved costs for given date.
        If yes,
        """
        if not delete_verified and DailyCost.objects.filter(
            date=date,
            verified=True
        ).count():
            raise VerifiedDailyCostsExistsError()
        DailyCost.objects.filter(date=date).delete()

    def _save_costs(self, date, costs, forecast):
        """
        For every service environment in costs save tree structure in database
        """
        for service_environment, se_costs in costs.iteritems():
            DailyCost.build_tree(
                tree=se_costs,
                date=date,
                service_environment_id=service_environment,
                forecast=forecast,
            )

    def _collect_costs(self, date, service_environments, forecast):
        """
        Collects costs from all plugins and stores them per service environment
        """
        logger.debug("Getting report date")
        old_queries_count = len(connection.queries)
        data = {se.id: [] for se in service_environments}
        for i, plugin in enumerate(self.get_plugins()):
            try:
                plugin_old_queries_count = len(connection.queries)
                plugin_report = plugin_runner.run(
                    'scrooge_costs',
                    plugin.plugin_name,
                    service_environments=service_environments,
                    date=date,
                    forecast=forecast,
                    type='costs',
                    **plugin.get('plugin_kwargs', {})
                )
                for service_id, service_usage in plugin_report.iteritems():
                    if service_id in data:
                        data[service_id].extend(service_usage)
                plugin_queries_count = (
                    len(connection.queries) - plugin_old_queries_count
                )
                if settings.DEBUG:
                    logger.debug('Plugin SQL queries: {0}\n'.format(
                        plugin_queries_count
                    ))
            except KeyError:
                logger.warning(
                    "Usage '{0}' has no usage plugin\n".format(plugin.name)
                )
            except NoPriceCostError:
                logger.warning('No costs defined\n')
            except MultiplePriceCostError:
                logger.warning('Multiple costs defined\n')
            except Exception as e:
                logger.exception(
                    "Error while generating the report: {0}\n".format(e)
                )
                raise

        queries_count = len(connection.queries) - old_queries_count
        if settings.DEBUG:
            logger.debug('Total SQL queries: {0}'.format(queries_count))
        return data

    @classmethod
    def _get_services_environments(cls):
        """
        This function return all ventures for which report will be ganarated

        :param boolean is_active: Flag. Get only active or all.
        :returns list: list of ventures
        :rtype list:
        """
        logger.debug("Getting services environments")
        services = ServiceEnvironment.objects.select_related(
            'service',
            'environment',
        ).order_by(
            'service__name',
            'environment__name',
        )
        logger.debug("Got {0} services".format(services.count()))
        return services

    @classmethod
    @memoize
    def get_plugins(cls):
        """
        Returns list of plugins to call, with information and extra cost about
        each, such as name and arguments
        """
        extra_cost_plugins = cls._get_extra_cost_plugins()
        base_usage_types_plugins = cls._get_base_usage_types_plugins()
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins()
        services_plugins = cls._get_pricing_services_plugins()
        teams_plugins = cls._get_teams_plugins()
        plugins = (base_usage_types_plugins + regular_usage_types_plugins +
                   services_plugins + teams_plugins +
                   extra_cost_plugins)
        return plugins

    @classmethod
    def _get_base_usage_types(cls, filter_=None):
        """
        Returns base usage types which should be visible on report
        """
        logger.debug("Getting usage types")
        query = UsageType.objects.filter(
            show_in_services_report=True,
            usage_type='BU',
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
            show_in_services_report=True,
            usage_type='RU',
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
    def _get_pricing_services(cls):
        """
        Returns services which should be visible on report
        """
        return PricingService.objects.order_by('name')

    @classmethod
    def _get_pricing_services_plugins(cls):
        """
        Returns plugins information (name and arguments) for services
        """
        pricing_services = cls._get_pricing_services()
        result = []
        for pricing_service in pricing_services:
            pricing_service_info = AttributeDict(
                name=pricing_service.name,
                plugin_name=pricing_service.get_plugin_name(),
                plugin_kwargs={
                    'pricing_service': pricing_service
                }
            )
            result.append(pricing_service_info)
        return result

    @classmethod
    def _get_teams(cls):
        """
        Returns teams which should be visible on report
        """
        return Team.objects.filter(show_in_report=True).order_by('name')

    @classmethod
    def _get_teams_plugins(cls):
        """
        Returns information about team plugins for each team
        """
        teams = cls._get_teams()
        result = []
        for team in teams:
            team_info = AttributeDict(
                name=team.name,
                plugin_name='team',
                plugin_kwargs={
                    'team': team
                }
            )
            result.append(team_info)
        return result

    @classmethod
    def _get_extra_costs(cls):
        """
        Returns all extra costs
        """
        return ExtraCostType.objects.order_by('name')

    @classmethod
    def _get_extra_cost_plugins(cls):
        """
        Returns information about extra cost plugins for each extra cost
        """
        extra_costs = cls._get_extra_costs()
        result = []
        for extra_cost in extra_costs:
            extra_cost_info = AttributeDict(
                name=extra_cost.name,
                plugin_name='extra_cost_plugin',
                plugin_kwargs={
                    'extra_cost_type': extra_cost,
                }
            )
            result.append(extra_cost_info)
        return result
