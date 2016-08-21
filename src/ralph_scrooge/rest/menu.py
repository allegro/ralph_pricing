# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response


class SubMenu(APIView):
    def get(self, request, format=None):
        menu = [
            {
                'name': 'Components',
                'href': '#/components/',
                'leftMenu': ['services'],
                'calendarMenu': 'daily',
                'auto_choose_env': False,
                'hide_envs_for_tabs': [],
            },
            {
                'name': 'Cost card',
                'href': '#/costcard/',
                'leftMenu': ['services'],
                'calendarMenu': 'monthly',
                'auto_choose_env': True,
                'hide_envs_for_tabs': [],
            },
            {
                'name': 'Components costs',
                'href': '#/costs/',
                'leftMenu': ['services'],
                'calendarMenu': 'range',
                'auto_choose_env': True,
                'hide_envs_for_tabs': [],
            },
            {
                'name': 'Allocations',
                'href': '#/allocation/client/',
                'leftMenu': ['services', 'teams'],
                'calendarMenu': 'monthly',
                'auto_choose_env': True,
                'hide_envs_for_tabs': ['serviceDivision'],
            },
        ]
        if request.user.is_superuser:
            menu.extend([
                {
                    'name': 'Allocations admin',
                    'href': '#/allocation/admin/',
                    'leftMenu': [],
                    'calendarMenu': 'monthly',
                    'auto_choose_env': True,
                    'hide_envs_for_tabs': [],
                },
                {
                    'name': 'Costs report',
                    'href': '/services-costs-report',
                },
                {
                    'name': 'Usages report',
                    'href': '/services-usages-report',
                },
                {
                    'name': 'Collect plugins',
                    'href': '/collect-plugins',
                },
                {
                    'name': 'Services changes report',
                    'href': '/services-changes-report',
                },
                {
                    'name': 'Costs calculation',
                    'href': '/monthly-costs',
                },
            ])
        return Response(menu)
