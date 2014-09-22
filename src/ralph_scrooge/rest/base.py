#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from ralph.util.views import jsonify


@csrf_exempt
@jsonify
def left_menu(request, *args, **kwargs):
    return {'user': request.user.username}
