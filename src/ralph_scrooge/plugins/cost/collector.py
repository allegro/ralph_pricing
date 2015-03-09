# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from dateutil import rrule

from django.conf import settings
from django.db import connection

from ralph.util import plugin as plugin_runner
from ralph_scrooge.models import (
    CostDateStatus,
    DailyCost,
    DynamicExtraCostType,
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
from ralph_scrooge.utils.common import memoize, AttributeDict

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
    def process_period(
        self,
        start,
        end,
        forecast,
        force_recalculation=False,
        **kwargs
    ):
        # calculate costs only if were not calculated for some date, unless
        # force_recalculation is True
        dates = self._get_dates(start, end, forecast, force_recalculation)
        for day in dates:
            try:
                self.process(
                    day,
                    forecast=forecast,
                    **kwargs
                )
                yield day, True
            except Exception as e:
                logger.exception(e)
                yield day, False

    def _get_dates(self, start, end, forecast, force_recalculation):
        """
        Return dates between start and end for which costs were not previously
        calculated.
        """
        days = [d.date() for d in rrule.rrule(
            rrule.DAILY,
            dtstart=start,
            until=end
        )]
        if force_recalculation:
            return days
        else:
            return sorted(set(days) - set(CostDateStatus.objects.filter(
                date__gte=start,
                date__lte=end,
                **{'forecast_calculated' if forecast else 'calculated': True}
            ).values_list('date', flat=True)))

    def process(
        self,
        date,
        forecast=False,
        delete_verified=False,
        plugins=None,
    ):
        """
        Process costs for single date.

        Process parts:
        1) collect costs from all plugins
        2) create DailyCost instances
        3) delete previously saved costs (if they were not verified, except
            sitution, where delete_verified=True was passed explicitly)
        4) save costs in database in tree format
        """
        logger.info('Calculating costs (forecast: {}) for date {}'.format(
            forecast,
            date,
        ))
        self._verify_accepted_costs(date, forecast, delete_verified)
        costs = self._collect_costs(
            date=date,
            forecast=forecast,
            plugins=plugins,
        )
        logger.info('Costs calculated for date {}'.format(date))
        return costs

    def save_period_costs(self, start, end, forecast, costs):
        """
        Save costs for period of time.

        :param costs: list of DailyCost instances
        """
        self._delete_daily_period_costs(start, end, forecast)
        self._save_costs(costs)
        self._update_status_period(start, end, forecast)
        logger.info('Costs saved for dates {}-{}'.format(start, end))

    def _delete_daily_period_costs(self, start, end, forecast):
        """
        Delete previously saved costs between start and end (including forecast
        flag).
        """
        logger.info('Deleting previously saved costs between {} and {}'.format(
            start,
            end,
        ))
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE FROM {}
            WHERE date>=%s and date<=%s and forecast=%s
            """.format(DailyCost._meta.db_table),
            [start, end, forecast]
        )

    def _verify_accepted_costs(self, date, forecast, delete_verified):
        """
        Verify if costs were already accepted for passed day. If yes and
        recalculation isn't forces VerifiedDailyCostsExistsError exception is
        raised.
        """
        if not delete_verified and CostDateStatus.objects.filter(
            date=date,
            **{'forecast_accepted' if forecast else 'accepted': True}
        ):
            raise VerifiedDailyCostsExistsError()

    def _create_daily_costs(self, date, costs, forecast):
        """
        For every service environment in costs create DailyCost instance to
        save it in database.
        """
        logger.info('Creating daily costs instances for {}'.format(date))
        daily_costs = []
        for service_environment, se_costs in costs.iteritems():
            # use _build_tree directly, to collect DailyCosts for all services
            # and save all at the end
            daily_costs.extend(DailyCost._build_tree(
                tree=se_costs,
                date=date,
                service_environment_id=service_environment,
                forecast=forecast,
            ))
        return daily_costs

    def _save_costs(self, daily_costs):
        """
        Save daily_costs in database.

        :param daily_costs: list instances of DailyCost
        """
        logger.info('Saving {} costs'.format(len(daily_costs)))
        DailyCost.objects.bulk_create(
            daily_costs,
            batch_size=settings.DAILY_COST_CREATE_BATCH_SIZE,
        )

    def _update_status(self, date, forecast):
        """
        Update status for given date that costs were caculated (including
        forecast flag).
        """
        # update status to created
        status, created = CostDateStatus.concurrent_get_or_create(date=date)
        if forecast:
            status.forecast_calculated = True
        else:
            status.calculated = True
        status.save()

    def _update_status_period(self, start, end, forecast):
        """
        Update status between start and end that costs were caculated
        (including forecast flag).
        """
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            self._update_status(day, forecast)

    def _collect_costs(
        self,
        date,
        forecast=False,
        plugins=None
    ):
        """
        Collects costs from all plugins and stores them per service environment
        """
        logger.debug("Getting report date")
        old_queries_count = len(connection.queries)
        data = defaultdict(list)
        for i, plugin in enumerate(plugins or self.get_plugins()):
            try:
                plugin_old_queries_count = len(connection.queries)
                plugin_report = plugin_runner.run(
                    'scrooge_costs',
                    plugin.plugin_name,
                    date=date,
                    forecast=forecast,
                    type='costs',
                    **{str(k): v for (k, v) in plugin['plugin_kwargs'].items()}
                )
                for service_id, service_usage in plugin_report.iteritems():
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
        services = ServiceEnvironment.objects.all()
        logger.debug("Got {0} services".format(services.count()))
        return services

    @classmethod
    @memoize
    def get_plugins(cls):
        """
        Returns list of plugins to call, with information and extra cost about
        each, such as name and arguments
        """
        extra_cost_types_plugins = cls._get_extra_cost_types_plugins()
        support_plugins = cls._get_support_plugins()
        dynamic_extra_cost_types_plugins = (
            cls._get_dynamic_extra_cost_types_plugins()
        )
        base_usage_types_plugins = cls._get_base_usage_types_plugins()
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins()
        services_plugins = cls._get_pricing_services_plugins()
        teams_plugins = cls._get_teams_plugins()
        plugins = (base_usage_types_plugins + regular_usage_types_plugins +
                   teams_plugins + support_plugins + extra_cost_types_plugins +
                   dynamic_extra_cost_types_plugins + services_plugins)
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
                }
            )
            result.append(rut_info)
        return result

    @classmethod
    def _get_pricing_services(cls):
        """
        Returns services which should be visible on report
        """
        return PricingService.objects.order_by('id')

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
                plugin_name='team_plugin',
                plugin_kwargs={
                    'team': team
                }
            )
            result.append(team_info)
        return result

    @classmethod
    def _get_extra_cost_types(cls):
        """
        Returns all extra costs (excluding supports)
        """
        # exclude supports (from fixture)
        return ExtraCostType.objects.exclude(pk=2).order_by('name')

    @classmethod
    def _get_extra_cost_types_plugins(cls):
        """
        Returns information about extra cost plugins for each extra cost
        """
        extra_costs = cls._get_extra_cost_types()
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

    @classmethod
    def _get_support_plugins(cls):
        return [
            AttributeDict(
                name='support',
                plugin_name='support_plugin',
                plugin_kwargs={},
            )
        ]

    @classmethod
    def _get_dynamic_extra_cost_types(cls):
        """
        Returns all extra costs
        """
        return DynamicExtraCostType.objects.order_by('name')

    @classmethod
    def _get_dynamic_extra_cost_types_plugins(cls):
        """
        Returns information about extra cost plugins for each extra cost
        """
        dynamic_extra_costs = cls._get_dynamic_extra_cost_types()
        result = []
        for dynamic_extra_cost in dynamic_extra_costs:
            dynamic_extra_cost_info = AttributeDict(
                name=dynamic_extra_cost.name,
                plugin_name='dynamic_extra_cost_plugin',
                plugin_kwargs={
                    'dynamic_extra_cost_type': dynamic_extra_cost,
                }
            )
            result.append(dynamic_extra_cost_info)
        return result
