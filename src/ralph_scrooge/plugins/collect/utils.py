# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.models import ServiceEnvironment
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)

from django.conf import settings
import requests


# TODO(xor-xor): Add tests for this function once responses lib will
# incorporate this bugfix: https://github.com/getsentry/responses/pull/109
# (or come up with some other tool to mock Ralph).
# TODO(mkurek): change query from string to dict
def get_from_ralph(endpoint, logger, query=None, limit=100):
    """Performs a GET request on Ralph's API endpoint, with optional query in
    form of 'key1=value1&key1=value2' and limit defaults to 100 (and since
    limit is a separate parameter, you shouldn't put it in the query string by
    yourself).
    """
    if query is None:
        url = "{}/{}/?limit={}".format(
            settings.RALPH3_API_BASE_URL.strip("/"), endpoint, limit
        )
    else:
        query = query.strip("?")
        url = "{}/{}/?limit={}&{}".format(
            settings.RALPH3_API_BASE_URL.strip("/"), endpoint, limit, query
        )
    headers = {
        "Authorization": "Token {}".format(settings.RALPH3_API_TOKEN),
        "Accept": "application/json",
    }
    while url:
        logger.debug("Performing GET request on {}.".format(url))
        resp = requests.get(url, headers=headers)
        if resp.status_code >= 400:
            msg = ("Got unexpected response from Ralph while accessing "
                   "'{}'. Status code: {}. Content: '{}'."
                   .format(url, resp.status_code, resp.content))
            logger.error(msg)
            return
        else:
            resp_contents = resp.json()
            url = resp_contents.get("next")
            for result in resp_contents.get("results", []):
                yield result


def get_unknown_service_env(plugin_type, subtype=None):
    """We assume that settings.UNKNOWN_SERVICES_ENVIRONMENTS structure can be
    be nested by one level at most.
    """
    val = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(plugin_type, (None, None))
    if isinstance(val, dict):
        if subtype is None:
            # 'subtype' param is required for nested structures here.
            raise UnknownServiceEnvironmentNotConfiguredError()
        else:
            val = val.get(subtype)
    service_uid, env_name = val
    unknown_service_env = None
    if service_uid:
        try:
            unknown_service_env = ServiceEnvironment.objects.get(
                service__ci_uid=service_uid,
                environment__name=env_name,
            )
        except ServiceEnvironment.DoesNotExist:
            pass
    if not unknown_service_env:
        raise UnknownServiceEnvironmentNotConfiguredError()
    return unknown_service_env
