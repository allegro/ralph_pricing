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
            },
            {
                'name': 'Allocations',
                'href': '#/allocation/client/',
                'leftMenu': ['services', 'teams'],
            },
            {
                'name': 'Allocations Admin',
                'href': '#/allocation/admin/',
                'leftMenu': [],
            }
            ####################################################
            # [DO NOT REMOVE!] THIS PART IS FOR NEXT FEATURES
            # ####################################################
            # {
            #     'name': 'Allocations',
            #     'href': '#/allocation/client/',
            #     'leftMenu': ['services', 'teams'],
            # },
            # {
            #     'name': 'Allocations Admin',
            #     'href': '#/allocation/admin/',
            #     'leftMenu': [],
            # }
            ####################################################
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
                    'name': 'Services changes report',
                    'href': '/scrooge/services-changes-report',
                },
                {
                    'name': 'Usage types',
                    'href': '/scrooge/usage-types',
                },
                {
                    'name': 'Extra Costs',
                    'href': '/scrooge/extra-costs',
                },
                {
                    'name': 'Collect plugins',
                    'href': '/scrooge/collect-plugins',
                },
                {
                    'name': 'Monthly costs',
                    'href': '/scrooge/monthly-costs',
                },
            ])
        return Response(menu)
