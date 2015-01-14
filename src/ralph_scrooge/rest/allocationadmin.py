#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from rest_framework.views import APIView
from rest_framework.response import Response

from ralph_scrooge.rest.common import get_dates
from ralph_scrooge.models import (
    UsageType,
    Warehouse,
    UsagePrice,
    TeamCost,
    Team,
)


class AllocationAdminContent(APIView):
    def _get_team_costs(self, start, end):
        rows = []
        for team in Team.objects.all():
            try:
                members, cost = TeamCost.objects.get(
                    team=team,
                    start=start,
                    end=end,
                ).value('members', 'cost')
            except:
                members, cost = 0, D(0)
            rows.append({
                'team': {
                    'id': team.id,
                    'name': team.name,
                },
                'cost': cost,
                'members': members,
            })
        return rows

    def _get_base_usages(self, start, end):
        rows = []
        warehouses = Warehouse.objects.filter(
            show_in_report=True,
        )
        for usage_type in UsageType.objects.filter(
            usage_type='BU',
            is_manually_type=True,
        ):
            if not usage_type.by_warehouse:
                try:
                    cost = UsagePrice.objects.get(
                        type=usage_type,
                        start=start,
                        end=end,
                    ).cost
                except UsagePrice.DoesNotExist:
                    cost = D(0)
                rows.append({
                    'type': {
                        'id': usage_type.id,
                        'name': usage_type.name,
                    },
                    'value': cost,
                })
            else:
                for warehouse in warehouses:
                    try:
                        cost = UsagePrice.objects.get(
                            type=usage_type,
                            start=start,
                            end=end,
                            warehouse=warehouse,
                        ).cost
                    except UsagePrice.DoesNotExist:
                        cost = D(0)
                    rows.append({
                        'type': {
                            'id': usage_type.id,
                            'name': usage_type.name,
                        },
                        'value': cost,
                        'warehouse': {
                            'id': warehouse.id,
                            'name': warehouse.name,
                        }
                    })
        return rows

    def get(self, request, month, year, format=None):
        first_day, last_day, days_in_month = get_dates(year, month)
        base_usages = self._get_base_usages(first_day, last_day)
        team_costs = self._get_team_costs(first_day, last_day)
        return Response({
            'baseusages': {
                'name': 'Base Usages',
                'rows': base_usages,
                'template': 'tabbaseusages.html',
            },
            'teamcosts': {
                'name': 'Team Costs',
                'rows': team_costs,
                'template': 'tabteamcosts.html',
            },
            'extracosts': {
                'name': 'Extra Costs',
                'rows': [{'extra_cost': 4, 'value': 400}],
                'template': 'tabextracosts.html',
            },
        })
