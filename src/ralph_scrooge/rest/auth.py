# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import permissions
from rest_framework.authentication import (
    TokenAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import (
    AuthenticationFailed
)

from ralph_scrooge.utils.security import (
    has_permission_to_team,
    has_permission_to_service,
)


class TastyPieLikeTokenAuthentication(TokenAuthentication):
    """
    A subclass of TokenAuthentication, which also supports TastyPie-like
    auth tokens, i.e.:

        Authorization: ApiKey username:401f7ac837da42b97f613d789819ff93537bee6a

    and

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a

    instead of just the latter (DjRF-like). In the former case, the "username:"
    component is silently discarded.
    """
    keywords = ('ApiKey', 'Token')

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        for keyword in self.keywords:
            if auth and auth[0].lower() == keyword.lower().encode():
                break
        else:
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = (
                'Invalid token header. Token string should not contain spaces.'
            )
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].split(':')[-1].decode()
        except UnicodeError:
            msg = (
                'Invalid token header. Token string should not contain '
                'invalid characters.'
            )
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)


class IsTeamLeader(permissions.BasePermission):
    """A permission class that is an equivalent of `team_permission` wrapper
    (from ralph_scrooge.utils.security) that is meant to use with API - the
    difference between these two is that in case of failue (i.e. when user
    doesn't have required permissions), the former redirects to login page,
    while the latter responds with 403. Can be extended to get service_uid
    from request's payload, if needed.
    """

    def has_permission(self, request, view):
        team_id = view.kwargs.get('team_id')
        if team_id is None:
            return True
        return has_permission_to_team(request.user, team_id)


class IsServiceOwner(permissions.BasePermission):
    """Checks if given user is an owner of the service given by service_uid
    that is coming in request's payload. Can easily be extended to get
    service_uid from URL.
    """

    def has_permission(self, request, view):
        service_uid = request.data.get('service_uid')
        if service_uid is None:
            return True
        return has_permission_to_service(
            request.user, service_uid, check_by_uid=True
        )
