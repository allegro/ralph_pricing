# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.report.base import BaseReportPlugin

logger = logging.getLogger(__name__)


@register(chain='scrooge_reports')
class UsageTypePlugin(BaseReportPlugin):
    """
    Usage Type reports plugin
    """
    base_usage_cost_symbol = 'cost_{0}'
    base_usage_count_symbol = 'count_{0}'

    def usages(
        self,
        start,
        end,
        usage_type,
        service_environments=None,
        *args,
        **kwargs
    ):
        usages_query = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if service_environments:
            usages_query = usages_query.filter(
                service_environment__in=service_environments,
            )
        usages = usages_query.values(
            'service_environment_id',
            'date',
        ).annotate(
            total=Sum('value'),
        )

        result = defaultdict(dict)
        for u in usages:
            result[u['date']][u['service_environment_id']] = u['total']
        return result

    def usages_schema(self, usage_type, *args, **kwargs):
        return _("{0} count".format(usage_type.name))
