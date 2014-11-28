# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import math
from datetime import date, timedelta
from optparse import make_option

from ralph_scrooge.management.commands._scrooge_base import ScroogeBaseCommand
from ralph_scrooge.models import DailyUsage, PRICING_OBJECT_TYPES


logger = logging.getLogger(__name__)


class Command(ScroogeBaseCommand):
    """
    Generate report with tenants instances of particular flavors
    """
    HEADERS = [
        'Service',
        'Environment',
        'OpenStack Tenant',
        'Model',
        'Flavor',
        'Instances',
    ]

    option_list = ScroogeBaseCommand.option_list + (
        make_option(
            '-t', '--today',
            dest='today',
            default=None,
            help="Date to generate report for",
        ),
    )

    def get_data(self, today, *args, **options):
        today = today or date.today() - timedelta(days=1)
        usages = DailyUsage.objects.filter(
            date=today,
            daily_pricing_object__pricing_object__type=(
                PRICING_OBJECT_TYPES.TENANT
            ),
            type__name__startswith='openstack.'
        ).values_list(
            'service_environment__service__name',
            'service_environment__environment__name',
            'daily_pricing_object__pricing_object__name',
            'daily_pricing_object__pricing_object__model__name',
            'type__name',
            'value',
        ).order_by('service_environment__service__name', 'type__name')
        result = []
        for usage in usages:
            u = list(usage)
            u[-1] = math.ceil(u[-1] / 24.0)  # get average instances in one day
            result.append(u)
        return result
