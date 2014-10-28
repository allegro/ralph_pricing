# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response

from ralph.account.models import Perm


class Menu(APIView):
    def get(self, request, format=None):
        menu = [
            {
                'name': 'Components',
                'href': '#/components/',
                'leftMenu': ['services'],
            },
            {
                'name': 'Allocations',
                'href': '#/allocation/client/',
                'leftMenu': ['services', 'teams'],
            }
        ]
        profile = request.user.get_profile()
        if profile.has_perm(Perm.has_scrooge_access) or profile.is_superuser:
            menu.extend([
                {
                    'name': 'Costs report',
                    'href': 'services-costs-report',
                },
                {
                    'name': 'Usages report',
                    'href': 'services-usages-report',
                },
                {
                    'name': 'Services changes report',
                    'href': 'services-changes-report',
                },
                {
                    'name': 'Usage types',
                    'href': 'usage-types',
                },
                {
                    'name': 'Extra Costs',
                    'href': 'extra-costs',
                },
                {
                    'name': 'Collect plugins',
                    'href': 'collect-plugins',
                },
                {
                    'name': 'Monthly costs',
                    'href': 'monthly-costs',
                },
            ])
        return Response(menu)
