import logging

from django.conf import settings

request_logger = logging.getLogger('ralph.request_user')


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

    def process_response(self, request, response):
        if request.path not in getattr(
            settings, 'LOGGER_REQUEST_DISABLED_PATHS', []
        ):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user_pk = request.user.pk
                username = request.user.username
            else:
                user_pk = -1
                username = 'anonymous'
            params = dict(
                user_pk=user_pk,
                username=username,
                path=request.path,
                method=request.method,
                response_code=response.status_code,
                source_ip=self._get_client_ip(request),
                ralph_host=request.get_host(),
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )
            request_logger.info(
                "Request: user: {user_pk} / {username} ; path: {path} ; "
                "method: {method} ; response code: {response_code} ; "
                "IP: {source_ip}; Ralph Host: {ralph_host}, "
                "User agent: {user_agent}".format(
                    **params
                ),
                extra=params,
            )
        return response
