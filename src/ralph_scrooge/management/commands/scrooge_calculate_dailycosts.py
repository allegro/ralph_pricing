# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.models import (
    CostDateStatus,
    PricingService,
    PricingServicePlugin,
)

logger = logging.getLogger(__name__)
yesterday = date.today() - timedelta(days=1)


class Command(BaseCommand):
    """Calculate daily costs for a given day (defaults to yesterday) and
    pricing service (defaults to all which are bot active and have fixed
    price).
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            dest='date',
            default=yesterday,
            help=_('Date to which calculate daily costs for')
        )
        parser.add_argument(
            '--forecast',
            dest='forecast',
            default=False,
            action='store_true',
            help=_('Use forecast prices and costs')
        )
        parser.add_argument(
            '--force',
            dest='force',
            default=False,
            action='store_true',
            help=_(
                "Force recalculation of costs. Doesn't apply to costs that "
                "are already accepted."
            )
        )
        parser.add_argument(
            '-p',
            dest='pricing_service_names',
            action='append',
            type=str,
            default=[],
            help=_(
                'Pricing Service name(s) to which calculate daily costs for'
            )
        )

    def _has_calculated_costs(self, date_, forecast):
        return CostDateStatus.objects.filter(
            date=date_,
            **{'forecast_calculated' if forecast else 'calculated': True}
        ).exists()

    def _has_accepted_costs(self, date_, forecast):
        return CostDateStatus.objects.filter(
            date=date_,
            **{'forecast_accepted' if forecast else 'accepted': True}
        ).exists()

    def _calculate_costs(self, date_, forecast, pricing_service_names, force):
        collector = Collector()

        # By default, take all PricingServices that are active and have fixed
        # price...
        query_params = {
            'active': True,
            'plugin_type': PricingServicePlugin.pricing_service_fixed_price_plugin.id,  # noqa: E501
        }
        # ...but when `-p` option is present, take only PricingServices
        # specified with it.
        if len(pricing_service_names) > 0:
            query_params.update({'name__in': pricing_service_names})
        pricing_services = PricingService.objects.filter(**query_params)
        pricing_service_names_verified = pricing_services.values_list(
            'name', flat=True
        )

        # Perform some basic sanity checks.
        if len(pricing_service_names_verified) != len(pricing_service_names):
            unknown_names = (
                set(pricing_service_names) - set(pricing_service_names_verified)  # noqa: E501
            )
            logger.warning(
                "Unknown Pricing Service name(s): {}."
                .format(", ".join(unknown_names))
            )
        if len(pricing_service_names_verified) == 0:
            logger.error(
                "No Pricing Service(s) that are both active and have fixed "
                "price. Aborting."
            )
            return
        if self._has_accepted_costs(date_, forecast):
            msg = (
                "The costs for the selected date and pricing service are "
                "already calculated and accepted."
            )
            if force:
                msg = " ".join(
                    (msg, "'--force' option can't be used here.")
                )
            logger.error(" ".join((msg, "Aborting.")))
            return
        if not force and self._has_calculated_costs(date_, forecast):
            logger.error(
                "The costs for the selected date and pricing service are "
                "already calculated. If you need to re-calculate them, use "
                "'--force' option. Aborting."
            )
            return

        plugins = [
            p for p in collector.get_plugins()
            if p.name in pricing_service_names_verified
        ]
        collector.calculate_daily_costs_for_day(date_, forecast, plugins)

    def _parse_date(self, date_):
        if not isinstance(date_, date):
            return datetime.strptime(date_, '%Y-%m-%d').date()
        else:
            return date_

    def handle(self, *args, **options):
        date_ = self._parse_date(options['date'])
        self._calculate_costs(
            date_,
            options['forecast'],
            options['pricing_service_names'],
            options['force'],
        )
