# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class PricingServiceUsages(APIView):

    def post(self, request, *args, **kwargs):
        result = {
            'status': 'ok',
            'message': 'success!',
        }
        return Response(result)
