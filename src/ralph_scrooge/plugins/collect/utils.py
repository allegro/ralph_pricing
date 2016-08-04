# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
import requests


def get_from_ralph(endpoint, logger, query=None):
    if query is None:
        url = "{}/{}/".format(
            settings.RALPH3_API_BASE_URL.strip("/"), endpoint
        )
    else:
        url = "{}/{}/?{}".format(
            settings.RALPH3_API_BASE_URL.strip("/"), endpoint, query
        )
    headers = {
        "Authorization": "Token {}".format(settings.RALPH3_API_TOKEN),
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers)  # XXX pagination..?
    if resp.status_code >= 400:
        msg = ("Got unexpected response from Ralph while accessing "
               "'{}'. Status code: {}. Content: '{}'."
               .format(url, resp.status_code, resp.content))
        logger.error(msg)
        return []
    else:
        return resp.json().get("results", [])
