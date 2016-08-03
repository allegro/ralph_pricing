# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db.transaction import commit_on_success
import requests

from ralph.util import plugin  # XXX to be replaced later..?
from ralph_scrooge.models import BusinessLine


logger = logging.getLogger(__name__)

def get_business_lines():
    url = "{}/{}/".format(
        settings.RALPH3_API_BASE_URL.strip("/"), "business-segments"
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


@commit_on_success
def update_business_line(bl):
    updated = False
    business_line, created = BusinessLine.objects.get_or_create(
        ci_id=bl['id'],
    )
    if not created and business_line.name != bl['name']:
        business_line.name = bl['name']
        business_line.save()
        updated = True
    return created, updated


@plugin.register(chain='scrooge', requires=[])
def business_line(today, **kwargs):  # XXX 'today' is unused
    new_bl = updated_bl = total = 0
    for bl in get_business_lines():
        created, updated = update_business_line(bl)
        if created:
            new_bl += 1
        if updated:
            updated_bl += 1
        total += 1
    return True, '{} new business line(s), {} updated, {} total'.format(
        new_bl,
        updated_bl,
        total,
    )
