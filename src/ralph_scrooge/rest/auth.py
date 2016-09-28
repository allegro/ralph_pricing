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
    """
    """

    def has_permission(self, request, view):
        from ralph_scrooge.models import Team, TeamManager
        team_id = view.kwargs['team_id']
        # XXX to be implemented
        from IPython import embed; embed(); assert False
        return True
