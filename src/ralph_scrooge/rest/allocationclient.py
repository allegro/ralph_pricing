#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.transaction import commit_on_success
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.rest.common import get_dates
from ralph_scrooge.models import (
    DailyUsage,
    ExtraCost,
    ExtraCostType,
    PricingService,
    Service,
    ServiceEnvironment,
    ServiceUsageTypes,
    Team,
    TeamCost,
    TeamServiceEnvironmentPercent,
    UsageType,
)
from ralph_scrooge.csvutil import parse_csv


class CannotDetermineValidServiceUsageTypeError(APIException):
    status_code = 400
    default_detail = 'Cannot determine valid (single!) service usage type'


def get_allocation_from_file(file, allocation_admin=False):
    """
    Parse CSV files from Python File object (file())
    It then search ServiceEnvironment based on the values in the service field.
    Returns list of usages (compatible with JSON sent by Scroge GUI)

    Args:
        file: Python File Object with structures:
            service_uid or service_env_id;environment;value;forecast_cost;cost
            sc-001;prod;10.0
            sc-002;prod;90.0
        allocation_admin: Validate allocation admin columns header,
            if Falase validate allocation client columns
    Return:
        list: Example data:
            [
                {
                    'service': service_environment,
                    'env': service_environment,
                    'value': '10.00',
                },
                ...
            ]
    """
    file_results = []
    headers, data_results = parse_csv(file)
    errors = []

    if not (
        'service_env_id' in headers or
        (
            ('service_uid' in headers or 'service_name' in headers) and
            'environment' in headers
        )
    ):
        errors.append(
            _('Missing columns: service_env_id or service_uid and environment')
        )

    if allocation_admin:
        if 'cost' not in headers:
            errors.append(_('Cost column not found in file headers.'))
    else:
        if 'value' not in headers:
            errors.append(_('Value column not found in file headers.'))

    if errors:
        return ({}, errors)

    for row in data_results:
        query = {}
        if row.get('service_env_id'):
            query['pk'] = row['service_env_id']
        else:
            if row.get('service_uid'):
                query['service__ci_uid'] = row['service_uid']
            else:
                query['service__name'] = row['service_name']

            query['environment__name'] = row['environment']

        try:
            service_env = ServiceEnvironment.objects.get(**query)
        except ServiceEnvironment.DoesNotExist:
            error = (
                'Service environment for service: {}, environment: '
                '{} does not exist.'
            ).format(
                row.get('service_uid', row.get('service_name')),
                row['environment']
            )
            errors.append(error)
            service_env = ''

        row_data = {
            'service': service_env,
            'env': service_env
        }
        if row.get('value'):
            row_data.update({'value': row['value']})
        if row.get('forecast_cost'):
            # get(.., 0) or 0 because forecast_cost may be empty
            row_data.update({
                'forecast_cost': row.get('forecast_cost', 0) or 0
            })
        if row.get('cost'):
            row_data.update({'cost': row['cost']})
        file_results.append(row_data)

    return (file_results, errors)


class AllocationClientService(APIView):
    def _get_service_usage_type(
        self,
        service,
        year,
        month,
        create_if_not_exist=False
    ):
        service = Service.objects.get(id=service)
        try:
            pricing_service = PricingService.objects.get(
                services=service
            )
        except PricingService.DoesNotExist:
            if not create_if_not_exist:
                return None
            pricing_service = PricingService.objects.create(
                name=service.name + '_pricing_service',
                symbol=(
                    service.symbol or
                    service.name.lower().replace(' ', '_') + '_pricing_service'
                )
            )
            pricing_service.services.add(service)

        start_date = date(int(year), int(month), 1)
        end_date = start_date + relativedelta(months=1) - timedelta(days=1)
        try:
            service_usage_type = ServiceUsageTypes.objects.get(
                pricing_service=pricing_service,
                start__lte=start_date,
                end__gte=end_date,
            )
        except ServiceUsageTypes.DoesNotExist:
            if not create_if_not_exist:
                return None
            usage_type = UsageType.objects.create(
                name=service.name + '_usage_type',
                symbol=(
                    service.symbol or
                    service.name.lower().replace(' ', '_') + '_usage_type'
                ),
            )
            dates = self._get_new_service_usage_type_max_daterange(
                pricing_service,
                start_date,
                end_date,
            )
            service_usage_type = ServiceUsageTypes.objects.create(
                usage_type=usage_type,
                pricing_service=pricing_service,
                start=dates[0],
                end=dates[1]
            )
        except ServiceUsageTypes.MultipleObjectsReturned:
            raise CannotDetermineValidServiceUsageTypeError()

        return service_usage_type

    def _get_new_service_usage_type_max_daterange(
        self,
        pricing_service,
        start_date,
        end_date
    ):
        """
        Returns maximum daterange (tuple) for newly created service usage type
        """
        try:
            new_start_date = ServiceUsageTypes.objects.filter(
                end__lte=start_date
            ).order_by('-end')[:1].get().end + timedelta(days=1)
        except ServiceUsageTypes.DoesNotExist:
            new_start_date = date.min

        try:
            new_end_date = ServiceUsageTypes.objects.filter(
                start__gte=start_date
            ).order_by('start')[:1].get().start - timedelta(days=1)
        except ServiceUsageTypes.DoesNotExist:
            new_end_date = date.max

        return new_start_date, new_end_date

    def _get_service_divison(self, service, year, month, first_day):
        service_usage_type = self._get_service_usage_type(service, year, month)

        rows = []
        if service_usage_type:
            for daily_usage in DailyUsage.objects.filter(
                date=first_day,
                type=service_usage_type.usage_type,
            ).select_related(
                "service_environment",
            ):
                rows.append({
                    "service": daily_usage.service_environment.service_id,
                    "env": daily_usage.service_environment.environment_id,
                    "value": daily_usage.value
                })
        return rows

    def _get_service_extra_cost(self, service, env, start, end):
        extra_costs = ExtraCost.objects.filter(
            start=start,
            end=end,
            service_environment=ServiceEnvironment.objects.get(
                service__id=service,
                environment__id=env,

            ),
            extra_cost_type=1  # ExtraCostType.objects_admin.get(name="other")
        )
        rows = []
        for extra_cost in extra_costs:
            rows.append({
                "id": extra_cost.id,
                "value": round(extra_cost.cost, 2),
                "remarks": extra_cost.remarks,
            })
        return rows

    def _clear_daily_usages(
        self,
        usage_type,
        first_day,
        last_day,
    ):
        DailyUsage.objects.filter(
            date__gte=first_day,
            date__lte=last_day,
            type=usage_type,
        ).delete()

    def get(self, request, year, month, service, env, *args, **kwargs):
        first_day, last_day, days_in_month = get_dates(year, month)
        response = {
            "serviceExtraCost": {
                "name": "Extra Cost",
                "template": "tabextracosts.html",
                "rows": self._get_service_extra_cost(
                    service,
                    env,
                    first_day,
                    last_day,
                ),
            },
        }
        try:
            response.update({
                "serviceDivision": {
                    "name": "Service Division",
                    "template": "taballocationclientdivision.html",
                    "rows": self._get_service_divison(
                        service,
                        year,
                        month,
                        first_day,
                    ),
                }
            })
        except CannotDetermineValidServiceUsageTypeError:
            pass

        return Response(response)

    @commit_on_success()
    def post(self, request, year, month, service, env, *args, **kwargs):
        if request.FILES and kwargs.get('allocate_type') == 'servicedivision':
            rows, errors = get_allocation_from_file(request.FILES['file'])
            if errors:
                return Response({'status': False, 'errors': errors})

            post_data = {
                'rows': rows
            }
        else:
            post_data = request.DATA

        first_day, last_day, days_in_month = get_dates(year, month)
        if kwargs.get('allocate_type') == 'servicedivision':
            service_usage_type = self._get_service_usage_type(
                service,
                year,
                month,
                create_if_not_exist=True
            )
            self._clear_daily_usages(
                service_usage_type.usage_type,
                first_day,
                last_day,
            )
            for row in post_data['rows']:
                if isinstance(row['service'], ServiceEnvironment):
                    service_environment = row['service']
                else:
                    service_environment = ServiceEnvironment.objects.get(
                        service__id=row['service'],
                        environment__id=row['env']
                    )
                for day in xrange(days_in_month):
                    iter_date = first_day + timedelta(days=day)
                    dpo = (
                        service_environment.dummy_pricing_object
                        .get_daily_pricing_object(iter_date)
                    )
                    DailyUsage.objects.create(
                        date=iter_date,
                        service_environment=service_environment,
                        daily_pricing_object=dpo,
                        value=row['value'],
                        type=service_usage_type.usage_type,
                    )
        if kwargs.get('allocate_type') == 'serviceextracost':
            service_environment = ServiceEnvironment.objects.get(
                service__id=service,
                environment__id=env,
            )
            other_type = ExtraCostType.objects.get(id=1)
            ids = set()
            for row in post_data['rows']:
                ids.add(row.get('id'))
                extra_cost = ExtraCost.objects.get_or_create(
                    id=row.get('id'),
                    start=first_day,
                    end=last_day,
                    service_environment=service_environment,
                    extra_cost_type=other_type,
                    defaults=dict(
                        cost=row['value'],
                        remarks=row.get('remarks', '')
                    )
                )[0]
                extra_cost.cost = row['value']
                extra_cost.remarks = row.get('remarks', '')
                extra_cost.save()
            ExtraCost.objects.filter(
                start=first_day,
                end=last_day,
                service_environment=service_environment,
                extra_cost_type=other_type,
            ).exclude(id__in=ids).delete()
        return Response({"status": True})


class AllocationClientPerTeam(APIView):
    def _get_team_divison(self, team, start, end):
        rows = []
        for tsep in TeamServiceEnvironmentPercent.objects.filter(
            team_cost__team__id=team,
            team_cost__start=start,
            team_cost__end=end,
        ).select_related(
            "service_environment",
        ):
            rows.append({
                "id": tsep.id,
                "service": tsep.service_environment.service_id,
                "env": tsep.service_environment.environment_id,
                "value": tsep.percent
            })
        return rows

    def get(self, request, year, month, team, format=None, *args, **kwargs):
        first_day, last_day, days_in_month = get_dates(year, month)
        return Response({
            "teamDivision": {
                "name": "Team Division",
                "template": "taballocationclientdivision.html",
                "rows": self._get_team_divison(team, first_day, last_day),
            }
        })

    @commit_on_success()
    def post(self, request, year, month, team, *args, **kwargs):
        if request.FILES and team:
            rows, errors = get_allocation_from_file(request.FILES['file'])
            if errors:
                return Response({'status': False, 'errors': errors})

            post_data = {
                'rows': rows
            }
        else:
            post_data = request.DATA

        first_day, last_day, days_in_month = get_dates(year, month)

        try:
            team = Team.objects.get(id=team)
        except Team.DoesNotExist:
            return {'status': False, 'message': 'Team Does Not Exist.'}
        TeamServiceEnvironmentPercent.objects.filter(
            team_cost__team=team,
            team_cost__start=first_day,
            team_cost__end=last_day,
        ).delete()
        team_cost = TeamCost.objects.get_or_create(
            team=team,
            start=first_day,
            end=last_day,
        )[0]
        for row in post_data['rows']:
            if isinstance(row['service'], ServiceEnvironment):
                service_environment = row['service']
            else:
                service_environment = ServiceEnvironment.objects.get(
                    service__id=row.get('service'),
                    environment__id=row.get('env')
                )
            tsep = TeamServiceEnvironmentPercent.objects.get_or_create(
                team_cost=team_cost,
                service_environment=service_environment,
                defaults=dict(
                    percent=row.get('value'),
                )
            )[0]
            tsep.percent = row.get('value')
            tsep.save()

        return Response({"status": True})
