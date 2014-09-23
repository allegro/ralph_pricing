#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ralph.util.views import jsonify


@csrf_exempt
@jsonify
@require_http_methods(["POST"])
def left_menu(request, *args, **kwargs):
	return {'ok': True}
