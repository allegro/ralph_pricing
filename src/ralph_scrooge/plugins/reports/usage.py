# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict, OrderedDict
from datetime import datetime
from decimal import Decimal as D

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge import utils
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.reports.base import BaseReportPlugin
from ralph_scrooge.utils import AttributeDict

logger = logging.getLogger(__name__)


class UsageBasePlugin(BaseReportPlugin):
    def _incomplete_price(
        self,
        usage_type,
        start,
        end,
        warehouse=None,
        team=None
    ):
        """
        Calculate if for every day in report there is price defined for usage
        type

        :param list usage_type: usage type
        :param datetime start: Start date of the report
        :param datetime end: End date of the report
        :returns str: 'No price' or 'Incomplete price' or None (if all is ok)
        """
        total_days = (end - start).days + 1  # total report days
        ut_days = 0
        usage_prices = usage_type.usageprice_set.filter(
            end__gte=start,
            start__lte=end,
        )
        if usage_type.by_warehouse and warehouse:
            usage_prices = usage_prices.filter(warehouse=warehouse)
        if usage_type.by_team and team:
            usage_prices = usage_prices.filter(team=team)
        usage_prices = usage_prices.values('start', 'end').distinct()
        intervals = [(v['start'], v['end']) for v in usage_prices]
        sum_of_intervals = utils.sum_of_intervals(intervals)
        ut_days = sum(map(
            lambda k: (min(end, k[1]) - max(start, k[0])).days + 1,
            sum_of_intervals
        ))
        if ut_days == 0:
            return _('No price')
        if ut_days != total_days:
            return _('Incomplete price')

    def _get_total_cost_by_warehouses(
        self,
        start,
        end,
        services,
        usage_type,
        forecast=False,
        **kwargs
    ):
        """
        Returns total cost of usage for services for every warehouse (if usage
        type is by service).
        """
        if usage_type.by_warehouse:
            warehouses = self.get_warehouses()
        else:
            warehouses = [None]
        result = []
        total_cost = D(0)

        # remove from services ones that should not be taken into consideration
        # when calculating costs for this usage type (and should not be counted
        # to total usages count)
        if usage_type.excluded_services.count():
            services = list(
                set(services) - set(usage_type.excluded_services.all())
            )

        for warehouse in warehouses:
            usage_in_warehouse = 0
            cost_in_warehouse = 0
            usage_prices = usage_type.usageprice_set.filter(
                start__lte=end,
                end__gte=start,
                type=usage_type,
            )
            if warehouse:
                usage_prices = usage_prices.filter(warehouse=warehouse)
            usage_prices = usage_prices.order_by('start')
            # total sum of costs in period of time (group by start, end and
            # type)
            if usage_type.by_cost and not usage_type.by_warehouse:
                usage_prices = usage_prices.values(
                    'start',
                    'end',
                    'type',
                ).annotate(
                    cost=Sum('cost'),
                    forecast_cost=Sum('forecast_cost'),
                )
                usage_prices = [AttributeDict(up) for up in usage_prices]
                # sort by start date
                usage_prices = sorted(usage_prices, key=lambda x: x.start)
            for usage_price in usage_prices:
                if usage_type.by_cost:
                    price = self._get_price_from_cost(
                        usage_price,
                        forecast,
                        warehouse,
                        excluded_services=usage_type.excluded_services.all(),
                    )
                else:
                    if forecast:
                        price = usage_price.forecast_price
                    else:
                        price = usage_price.price

                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)

                total_usage = self._get_total_usage_in_period(
                    up_start,
                    up_end,
                    usage_type,
                    warehouse,
                    services
                )
                usage_in_warehouse += total_usage
                cost = D(total_usage) * price
                cost_in_warehouse += cost

            result.append(usage_in_warehouse)
            cost_in_warehouse = D(cost_in_warehouse)
            result.append(cost_in_warehouse)
            total_cost += cost_in_warehouse
        if usage_type.by_warehouse:
            result.append(total_cost)
        return result

    def _get_usages_per_warehouse(
        self,
        usage_type,
        start,
        end,
        forecast,
        services,
        no_price_msg=False,
        use_average=True,
        by_device=False,
    ):
        """
        Returns information about usage (of usage type) count and cost
        per service in period (between start and end) using forecast or real
        price. If no_price_msg is False, then even if there is no price
        defined cost will always be number. If no_price_msg is True then if
        price for period of time in undefined of partially defined (incomplete)
        cost will be message what's wrong with price (i.e. 'Incomplete price').
        """
        excluded_services = usage_type.excluded_services.all()
        total_days = (end - start).days + 1  # total report days
        if usage_type.by_warehouse:
            warehouses = self.get_warehouses()
        else:
            warehouses = [None]
        result = defaultdict(lambda: defaultdict(int))

        def add_usages_per_service(
            up_start,
            up_end,
            price,
            warehouse,
            **kwargs
        ):
            usages_per_service = self._get_usages_in_period_per_service_environment(
                start=up_start,
                end=up_end,
                usage_type=usage_type,
                warehouse=warehouse,
                services=services,
                excluded_services=excluded_services,
            )
            for v in usages_per_service:
                service_environment = v['service_environment']
                result[service_environment][count_key] += v['usage']
                cost = D(v['usage']) * price
                if price_undefined:
                    result[service_environment][cost_key] = price_undefined
                else:
                    result[service_environment][cost_key] += cost
                if usage_type.by_warehouse and not price_undefined:
                    result[service_environment][total_cost_key] += cost

        def add_usages_per_device(
            up_start,
            up_end,
            price,
            warehouse,
            **kwargs
        ):
            usages_per_device = self._get_usages_in_period_per_device(
                start=up_start,
                end=up_end,
                usage_type=usage_type,
                services=services,
                warehouse=warehouse,
                excluded_services=excluded_services,
            )
            for v in usages_per_device:
                # TODO: rename
                device = v['daily_pricing_object__pricing_object']
                result[device][count_key] += v['usage']
                cost = D(v['usage']) * price
                if price_undefined:
                    result[device][cost_key] = price_undefined
                else:
                    result[device][cost_key] += cost
                if usage_type.by_warehouse and not price_undefined:
                    result[device][total_cost_key] += cost

        add_function = (
            add_usages_per_device if by_device else add_usages_per_service
        )

        for warehouse in warehouses:
            price_undefined = no_price_msg and self._incomplete_price(
                usage_type,
                start,
                end,
                warehouse
            )
            # get sum of cost in equal periods of time (ex. for internet
            # providers)
            usage_prices = usage_type.usageprice_set.filter(
                start__lte=end,
                end__gte=start,
            ).values(
                'start',
                'end',
                'type'
            ).annotate(
                price=Sum('price'),
                forecast_price=Sum('forecast_price'),
                forecast_cost=Sum('forecast_cost'),
                cost=Sum('cost')
            )
            if warehouse:
                usage_prices = usage_prices.filter(warehouse=warehouse)
            usage_prices = usage_prices.order_by('start')
            usage_prices = [AttributeDict(up) for up in usage_prices]

            if usage_type.by_warehouse:
                count_key = 'ut_{0}_count_wh_{1}'.format(
                    usage_type.id,
                    warehouse.id
                )
                cost_key = 'ut_{0}_cost_wh_{1}'.format(
                    usage_type.id,
                    warehouse.id
                )
                total_cost_key = 'ut_{0}_total_cost'.format(usage_type.id)
            else:
                count_key = 'ut_{0}_count'.format(usage_type.id)
                cost_key = 'ut_{0}_cost'.format(usage_type.id)

            if usage_prices:
                for usage_price in usage_prices:
                    if forecast:
                        price = usage_price.forecast_price
                    else:
                        price = usage_price.price
                    if usage_type.by_cost:
                        price = self._get_price_from_cost(
                            usage_price,
                            forecast,
                            warehouse,
                            excluded_services=excluded_services,
                        )

                    up_start = max(start, usage_price.start)
                    up_end = min(end, usage_price.end)
                    add_function(
                        up_start,
                        up_end,
                        warehouse=warehouse,
                        price=price
                    )
            else:
                add_function(start, end, warehouse=warehouse, price=0)

            if use_average and usage_type.average:
                for service, service_usages in result.iteritems():
                    service_usages[count_key] /= total_days

        return result

    def total_cost(self, *args, **kwargs):
        costs_by_wh = self._get_total_cost_by_warehouses(*args, **kwargs)
        return costs_by_wh[-1]

    def costs(
        self,
        start,
        end,
        services,
        usage_type,
        forecast=False,
        no_price_msg=False,
        use_average=True,
        **kwargs
    ):
        logger.debug("Get {0} usages".format(usage_type.name))
        return self._get_usages_per_warehouse(
            start=start,
            end=end,
            services=services,
            usage_type=usage_type,
            forecast=forecast,
            no_price_msg=no_price_msg,
            use_average=use_average,
        )

    def costs_per_device(
        self,
        start,
        end,
        services,
        usage_type,
        forecast=False,
        no_price_msg=False,
        use_average=True,
        **kwargs
    ):
        """
        Main method to get information about usages per device in service.
        """
        logger.debug("Getting {} costs per device".format(usage_type.name))
        return self._get_usages_per_warehouse(
            start=start,
            end=end,
            services=services,
            usage_type=usage_type,
            forecast=forecast,
            no_price_msg=no_price_msg,
            use_average=use_average,
            by_device=True,
        )

    def dailyusages(self, start, end, usage_type, services):
        """
        Returns sum of usage type per service per day. Result format:
            result = {
                day: {
                    service: value,
                    veture: value,
                    ...
                },
                ...
            }

        :rtype: dict
        """
        logger.debug(
            "Getting {0} daily usages per service".format(usage_type.name)
        )
        result = defaultdict(dict)
        dailyusages = usage_type.dailyusage_set.filter(
            service_environment__service__in=services,
            date__gte=start,
            date__lte=end,
        ).extra({
            'day': "date(date)"
        }).values(
            'day',
            'service_environment',
        ).annotate(
            usage=Sum('value')
        )
        for d in dailyusages:
            day = d['day']
            # on sqlite string is returned from query instead of datetime
            if isinstance(day, basestring):
                day = datetime.strptime(day, "%Y-%m-%d").date()
            result[day][d['service_environment']] = d['usage']
        return result

    def schema(self, usage_type, **kwargs):
        logger.debug("Get {0} schema".format(usage_type.name))
        if usage_type.by_warehouse:
            schema = OrderedDict()
            for warehouse in self.get_warehouses():
                count_key = 'ut_{0}_count_wh_{1}'.format(
                    usage_type.id,
                    warehouse.id
                )
                cost_key = 'ut_{0}_cost_wh_{1}'.format(
                    usage_type.id,
                    warehouse.id
                )
                schema[count_key] = {
                    'name': _("{0} count ({1})".format(
                        usage_type.name,
                        warehouse.name,
                    )),
                    'rounding': usage_type.rounding,
                    'divide_by': usage_type.divide_by,
                }
                schema[cost_key] = {
                    'name': _("{0} cost ({1})".format(
                        usage_type.name,
                        warehouse.name,
                    )),
                    'currency': True,
                }
            schema['ut_{0}_total_cost'.format(usage_type.id)] = {
                'name': _("{0} total cost".format(usage_type.name)),
                'currency': True,
                'total_cost': True,
            }
        else:
            schema = OrderedDict([
                ('ut_{0}_count'.format(usage_type.id), {
                    'name': _("{0} count".format(usage_type.name)),
                    'rounding': usage_type.rounding,
                    'divide_by': usage_type.divide_by,
                }),
                ('ut_{0}_cost'.format(usage_type.id), {
                    'name': _("{0} cost".format(usage_type.name)),
                    'currency': True,
                    'total_cost': True,
                }),
            ])
        return schema

    def schema_devices(self, **kwargs):
        """
        Returns schema for devices usages (which by default is the same as
        for services usages.
        """
        return self.schema(**kwargs)

    def dailyusages_header(self, usage_type):
        """
        Header for usage type column on dailyusages report.
        """
        return usage_type.name


@register(chain='reports')
class UsagePlugin(UsageBasePlugin):
    """
    Base Usage Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from UsageBasePlugin.
    """
    pass
