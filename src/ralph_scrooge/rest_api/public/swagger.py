# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os.path

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.generic import View


logger = logging.getLogger(__name__)


def _load_api_schema():
    json_schema_filename = os.path.splitext(
        os.path.basename(settings.API_SCHEMA_FILE)
    )[0] + '.json'

    json_schema_file = os.path.join(
        os.path.dirname(settings.API_SCHEMA_FILE),
        json_schema_filename
    )
    with open(json_schema_file, 'r') as f:
        contents = f.read()
    size = os.path.getsize(json_schema_file)
    return (contents, size)


try:
    API_SCHEMA, API_SCHEMA_SIZE = _load_api_schema()
except IOError as e:
    logger.error(
        'Problem with API schema file: {}. Switching to returning 404 status '
        'code instead.'.format(e)
    )
    API_SCHEMA = None


class BootstrapSwagger(View):

    def get(self, request):
        return render_to_response('swagger_ui_index.html')


class APISchema(View):
    """The purpose of this view is to serve static file with API schema.
    The reason for doing this in that particular way is that we need to exclude
    this file from any static files versioning mechanisms, which by appending
    hashes to file names will make this schema file unusable for external
    clients.

    And since this file is served from memory, it shouldn't impose any
    significant performance penalty (TODO(xor-xor): measure this).
    """

    def get(self, request):
        ct = 'application/json'
        if not API_SCHEMA:
            return HttpResponseNotFound(
                json.dumps({'error': 'API schema file could not be found'}),
                content_type=ct,
            )
        response = HttpResponse(API_SCHEMA, content_type=ct)
        response['Content-Disposition'] = "inline"
        response['Content-Length'] = API_SCHEMA_SIZE
        return response
