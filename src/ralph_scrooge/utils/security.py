# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden

from ralph_scrooge.models import ServiceOwnership, TeamManager


# TODO(xor-xor): Consider moving contents of this module into
# ralph_scrooge.rest_api.public.auth.

def _is_usage_owner(user):
    return (
        user.is_superuser or
        user.groups.filter(name=settings.USAGE_OWNERS_GROUP_NAME).exists()
    )


def usage_owner_permission(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if _is_usage_owner(request.user):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            json.dumps({'message': 'No permission to service'}),
            content_type="application/json"
        )
    return login_required(_wrapped_view)


def superuser_permission(view_func):
    """
    Check if user is superuser.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            json.dumps({'message': 'No permission to service'}),
            content_type="application/json"
        )
    return login_required(_wrapped_view)


# TODO(xor-xor): Make it "private" again, once this module get merged into
# ralph_scrooge.rest_api.public.auth.
def has_permission_to_service(user, service, check_by_uid=False):
    if user.is_superuser:
        return True
    if check_by_uid:
        return ServiceOwnership.objects.filter(
            service__ci_uid=service,
            owner=user,
        ).exists()
    return ServiceOwnership.objects.filter(
        service__id=service,
        owner=user,
    ).exists()


# TODO(xor-xor): Make it "private" again, once this module get merged into
# ralph_scrooge.rest_api.public.auth.
def has_permission_to_team(user, team):
    if user.is_superuser:
        return True
    return TeamManager.objects.filter(
        team__id=team,
        manager=user,
    ).exists()


def service_permission(view_func):
    """
    Wraps view to check, if user has access to passed service
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        # if we get here, user has scrooge permission
        if (
            (
                'service' in kwargs and
                has_permission_to_service(request.user, kwargs['service'])
            ) or
            'service' not in kwargs
        ):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            json.dumps({'message': 'No permission to service'}),
            content_type="application/json"
        )
    return login_required(_wrapped_view)


def team_permission(view_func):
    """
    Wraps view to check, if user has access to passed team
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        # if we get here, user has scrooge permission
        if (
            (
                'team' in kwargs and
                has_permission_to_team(request.user, kwargs['team'])
            ) or
            'team' not in kwargs
        ):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            json.dumps({'message': 'No permission to team'}),
            content_type="application/json"
        )
    return login_required(_wrapped_view)
