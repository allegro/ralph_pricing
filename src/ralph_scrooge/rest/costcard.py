# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from django.db.models import Sum
from django.utils.translation import ugettext as _
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from ralph_scrooge.models import (
    BaseUsage,
    CostDateStatus,
    DailyCost,
    ServiceEnvironment,
)
from ralph_scrooge.rest.common import get_dates


class CostCardContent(APIView):
    """
    Collect and sort all pre-generated costs per BaseUsage.
    """
    def get(self, request, service, env, month, year, format=None):
        """
        Collecting costs and format it for angular view.

        :param service int: service id
        :param env int: environment id
        :param month int: ordinal value of month
        :param year int: year
        :returns object: json response
        """
        first_day, last_day, days_in_month = get_dates(year, month)
        try:
            service_environment = ServiceEnvironment.objects.get(
                service__id=service,
                environment_id=env,
            )
        except ServiceEnvironment.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": _(
                        "Service {0} or environment {1} "
                        "does not exist".format(service, env)
                        )
                },
                status=HTTP_404_NOT_FOUND
            )
        forecast = request.QUERY_PARAMS.get('forecast', False)
        dates = CostDateStatus.objects.filter(
            date__gte=first_day,
            date__lte=last_day,
            **{'forecast_accepted' if forecast else 'accepted': True}
        ).values_list('date', flat=True)

        if len(dates) == 0:
            return Response({
                "status": False,
                "message": _(
                    'There are no accepted costs for chosen date.'
                    ' Please choose different date or back later.'
                )
            })

        monthly_costs = DailyCost.objects.filter(
            date__in=dates,
            service_environment=service_environment,
            forecast=forecast,
        ).values(
            'type'
        ).annotate(
            sum_cost=Sum('cost')
        )

        base_usages = {bu.id: bu.name for bu in BaseUsage.objects.all()}

        total = D(0)
        results = []
        for monthly_cost in monthly_costs:
            results.append({
                'name': base_usages[monthly_cost['type']],
                'cost': round(monthly_cost['sum_cost'], 2)
            })
            total += monthly_cost['sum_cost']
        results.append({
            'name': _('Total'),
            'cost': round(total, 2),
        })

        return Response({
            "status": True,
            "results": results
        })
