# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import coreapi  # XXX
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import renderers, response, schemas
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer  # XXX

schema = coreapi.Document(
    title='Scrooge API',
    content={
        'search': coreapi.Link(
            url='/search/',
            action='get',
            fields=[
                coreapi.Field(
                    name='from',
                    required=True,
                    location='query',
                    description='City name or airport code.'
                ),
                coreapi.Field(
                    name='to',
                    required=True,
                    location='query',
                    description='City name or airport code.'
                ),
                coreapi.Field(
                    name='date',
                    required=True,
                    location='query',
                    description='Flight date in "YYYY-MM-DD" format.'
                )
            ],
            description='Return flight availability and prices.'
        )
    }
)


@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    return response.Response(schema)


generator = schemas.SchemaGenerator(title='Bookings API')

@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_explicit_view(request):
    schema = generator.get_schema(request)
    return response.Response(schema)
