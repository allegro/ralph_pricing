#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import functools

from django.views.decorators.csrf import requires_csrf_token
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed,
    HttpResponseForbidden
)


def jsonify(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reply = func(*args, **kwargs)
        if isinstance(reply, HttpResponseRedirect):
            return reply
        if isinstance(reply, HttpResponseNotAllowed):
            return reply
        return HttpResponse(json.dumps(reply),
                            mimetype="application/javascript")
    return wrapper


@requires_csrf_token
def HTTP403(request, msg=None, template_name='403.html'):
    """
    A slightly customized version of 'permission_denied' handler taken from
    'django.views.defaults' (added 'REQUEST_PERM_URL' etc.).
    """
    if not msg:
        msg = _("You don't have permission to this resource.")
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    context = RequestContext(request, {
        'REQUEST_PERM_URL': getattr(settings, 'REQUEST_PERM_URL', None),
        'msg': msg,
    })
    return HttpResponseForbidden(template.render(context))