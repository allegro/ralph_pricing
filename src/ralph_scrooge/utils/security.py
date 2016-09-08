# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps, partial

from django import http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import loader, RequestContext, TemplateDoesNotExist
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token

from ralph.account.models import Perm, ralph_permission

from ralph_scrooge.models import ServiceOwnership, TeamManager


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
        return http.HttpResponseForbidden('<h1>403 Forbidden</h1>')
    context = RequestContext(request, {
        'REQUEST_PERM_URL': getattr(settings, 'REQUEST_PERM_URL', None),
        'msg': msg,
    })
    return http.HttpResponseForbidden(template.render(context))


def superuser_or_permission(view_func, perms):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return ralph_permission(perms)(view_func)(request, *args, **kwargs)
    return login_required(_wrapped_view)


scrooge_permission = partial(
    superuser_or_permission,
    perms=[
        {
            'perm': Perm.has_scrooge_access,
            'msg': _("You have no access to Scrooge!"),
        },
    ]
)


def _has_permission_to_service(user, service):
    profile = user.get_profile()
    # check for superuser or accountant, which have access to all services
    if user.is_superuser or profile.has_perm(Perm.has_scrooge_access):
        return True
    return ServiceOwnership.objects.filter(
        service__id=service,
        owner__profile__user=user,
    ).exists()


def _has_permission_to_team(user, team):
    profile = user.get_profile()
    # check for superuser or accountant, which have access to all services
    if user.is_superuser or profile.has_perm(Perm.has_scrooge_access):
        return True
    return TeamManager.objects.filter(
        team__id=team,
        manager__profile__user=user,
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
                _has_permission_to_service(request.user, kwargs['service'])
            ) or
            'service' not in kwargs
        ):
            return view_func(request, *args, **kwargs)
        return HTTP403(request, 'No permission to service')
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
                _has_permission_to_team(request.user, kwargs['team'])
            ) or
            'team' not in kwargs
        ):
            return view_func(request, *args, **kwargs)
        return HTTP403(request, 'No permission to team')
    return login_required(_wrapped_view)
