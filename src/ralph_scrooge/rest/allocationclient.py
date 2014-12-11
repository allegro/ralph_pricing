#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response


class AllocationClientContent(APIView):
    def get(self, request, service, env, year, month, format=None):
        return Response({
            'serviceDivision': {
                'name': 'Service division',
                'rows': [{'service': 97, 'env': 1, 'value': 100}],
                'template': 'tabservicedivision.html',
            },
            #'teamcosts': {
            #    'name': 'Team Costs',
            #    'rows': team_costs,
            #    'template': 'tabteamcosts.html',
            #},
            #'extracosts': {
            #    'name': 'Extra Costs',
            #    'rows': [{'extra_cost': 4, 'value': 400}],
            #    'template': 'tabextracosts.html',
            #},
        })
        # return Response([
        #     {
        #         'key': 'serviceDivision': {
        #         'name': 'Allocation',
        #         'rows': [{'service': 97, 'env': 2, 'value': 100}],
        #         'template': 'tabservicedivision.html',
        #     },
        #     'extracosts': {
        #         'name': 'Extra Costs',
        #         'rows': [{'id': 4, 'cost': 400, 'description': 'pizza'}],
        #         'template': 'tabextracosts.html',
        #     },
        # ])
