# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response

from ralph.account.models import Perm


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
                'name': 'Allocations',
                'href': '#/allocation/client/',
                'leftMenu': ['services', 'teams'],
                'calendarMenu': 'monthly',
                'auto_choose_env': True,
                'hide_envs_for_tabs': ['serviceDivision'],
            },
            {
                'name': 'Costs',
                'href': '#/costs/',
                'leftMenu': ['services', 'teams'],
                'calendarMenu': 'range',
                'auto_choose_env': True,
                'hide_envs_for_tabs': [],
            },
            {
                'name': 'Allocations Admin',
                'href': '#/allocation/admin/',
                'leftMenu': [],
                'calendarMenu': 'monthly',
                'auto_choose_env': True,
                'hide_envs_for_tabs': [],
            },
        ]
        profile = request.user.get_profile()
        if profile.has_perm(Perm.has_scrooge_access) or profile.is_superuser:
            menu.extend([
                {
                    'name': 'Costs report',
                    'href': '/scrooge/services-costs-report',
                },
                {
                    'name': 'Usages report',
                    'href': '/scrooge/services-usages-report',
                },
                {
                    'name': 'Collect plugins',
                    'href': '/scrooge/collect-plugins',
                },
                {
                    'name': 'Services changes report',
                    'href': '/scrooge/services-changes-report',
                },
                {
                    'name': 'Extra Costs',
                    'href': '/scrooge/extra-costs',
                },
                {
                    'name': 'Usage types',
                    'href': '/scrooge/usage-types',
                },
                {
                    'name': 'Monthly costs',
                    'href': '/scrooge/monthly-costs',
                },
            ])
        return Response(menu)
