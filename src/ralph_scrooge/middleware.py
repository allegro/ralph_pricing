from __future__ import absolute_import

import logging
import threading
import uuid

from django.conf import settings

request_logger = logging.getLogger('scrooge.request_user')
response_logger = logging.getLogger('scrooge.response_user')


class LogRequestUser(object):
    """
    Log each request with info such like user, HTTP method, source IP address,
    response status code.
    """
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_user_data(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            return request.user.pk, request.user.username
        else:
            return -1, 'anonymous'

    def should_log_request(self, request):
        return request.path not in getattr(
            settings, 'LOGGER_REQUEST_DISABLED_PATHS', []
        )

    def get_log_params(self, request, response=None):
        user_pk, username = self.get_user_data(request)
        params = dict(
            user_pk=user_pk,
            username=username,
            path=request.path,
            method=request.method,
            source_ip=self._get_client_ip(request),
            scrooge_host=request.get_host(),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )

        if response:
            params.update({'response_code': response.status_code})

        return params

    def process_request(self, request):
        if self.should_log_request(request):
            params = self.get_log_params(request)
            request_logger.info(
                "Request: user: {user_pk} / {username} ; path: {path} ; "
                "method: {method} ; "
                "IP: {source_ip}; Scrooge Host: {scrooge_host}, "
                "User agent: {user_agent}".format(
                    **params
                ),
                extra=params,
            )

    def process_response(self, request, response):
        if self.should_log_request(request):
            params = self.get_log_params(request, response)
            response_logger.info(
                "Response: user: {user_pk} / {username} ; path: {path} ; "
                "method: {method} ; response code: {response_code} ; "
                "IP: {source_ip}; Scrooge Host: {scrooge_host}, "
                "User agent: {user_agent}".format(
                    **params
                ),
                extra=params,
            )
        return response


local = threading.local()


def get_request_id():
    try:
        return local.request_id
    except AttributeError:
        return None


class RequestIDMiddleware(object):
    """Middleware used for storing request ID in thread local variable"""

    def process_request(self, request):
        local.request_id = uuid.uuid4().hex[:-10]

    def process_response(self, request, response):
        try:
            del local.request_id
        except AttributeError:
            pass
        return response


class AddRequestIDFilter(logging.Filter):

    def filter(self, record):
        record.__dict__.update({'request_id': get_request_id()})
        return True
