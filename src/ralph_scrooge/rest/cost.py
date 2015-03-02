#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework.views import APIView


class CostContent(APIView):
    def get(self, format=None, *args, **kwargs):
        return Response({
            'icon_class': 'fa-cloud-upload',
            'name': 'OpenStack Tenant',
            'color': '#009688',
            'value': [{
                '1': '5cache-dev',
                '0': 9388L,
                '3': 'OpenStack Tenant Essex',
                '2': 'f1130f817d044d6aa3f14472c3a1b7ed',
                '__nested': [{
                    '0': 'Cost Name',
                    '1': '123123',
                }]
                }, {
                    '1': '5cache-dev',
                    '0': 9579L,
                    '3': 'OpenStack Tenant Havana',
                    '2': '6b63df40fbe14dce83ea41cc2a7592ed'
                }
            ],
            'slug': 'openstack-tenant',
            'nested_schema': {
                '1': 'Name',
                '0': 'Cost',
            },
            'schema': {
                '1': 'Name',
                '0': 'Id',
                '3': 'Model Name',
                '2': 'Openstack Tenant Id'
            }
        })
