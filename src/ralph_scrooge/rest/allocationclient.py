#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ralph.util.views import jsonify

from ralph_scrooge.models import (
    ServiceUsageTypes,
)


def _get_service_usage_type(*args, **kwargs):
    return ServiceUsageTypes.objects.get(
        pricing_service__services__name=kwargs.get(
            'service',
        ),
    )


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def allocation_content(request, *args, **kwargs):
    service_usage_type = _get_service_usage_type(*args, **kwargs)
    return service_usage_type


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def allocation_save(request, *args, **kwargs):
    print (request.POST, args, kwargs)
    if kwargs.get('allocate_type') == 'servicedivision':
        return {'status': 'ok'}
