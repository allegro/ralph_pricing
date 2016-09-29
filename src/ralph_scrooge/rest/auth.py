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

from ralph_scrooge.utils.security import has_permission_to_team


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
        if request.method == 'GET':
            team_id = view.kwargs.get('team_id')
        elif request.method == 'POST':
            # XXX(xor-xor): I don't like the idea of touching request.DATA
            # here, but we need to obtain team_id somehow (maybe it should
            # be given in URL, as in GET case..?).
            team_id = request.DATA.get('team_id')
        if team_id is None:
            # XXX(xor-xor): ralph_scrooge.utils.security.team_permission
            # returns True in such case!
            return False
        return has_permission_to_team(request.user, team_id)
