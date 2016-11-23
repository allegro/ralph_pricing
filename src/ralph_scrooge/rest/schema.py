# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os import path

import coreapi  # XXX
from coreapi import Document, Field, Link  # XXX
from openapi_codec import OpenAPICodec
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import renderers, response, schemas
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer  # XXX

schema = Document(
    title='Scrooge API',
    url='',
    content={
        'v0.10': {
            'service-environment-costs': {
                'create': Link(
                    url='/scrooge/api/v0.10/service-environment-costs/',
                    action='post',
                    encoding='application/json',
                    fields=[
                        # XXX consider adding `description` field to Fields below
                        Field('service_uid', required=True, location='form'),
                        Field('environment', required=True, location='form'),
                        Field('date_from', required=True, location='form'),
                        Field('date_to', required=True, location='form'),
                        Field('group_by', required=True, location='form'),
                        Field('types', location='form', type='array'),
                        Field('forecast', location='form', type='boolean'),
                    ],
                    description=(
                        "Fetch daily costs for given service/environment "
                        "aggregated over given time period"
                    ),
                ),
            },
            'usage-types': {
                'list': Link(
                    url='/scrooge/api/v0.10/usage-types/',
                    action='get',
                    fields=[
                        Field('page', location='query'),
                    ],
                    description="Fetch all usage types",
                ),
                'read': Link(
                    url='/scrooge/api/v0.10/usage-types/{symbol}/',
                    action='get',
                    fields=[
                        Field('symbol', required=True, location='path'),
                    ],
                    description="Fetch usage type given by 'symbol'",
                ),
            },
        },
        'v0.9': {
            'api-token-auth': {
                'create': Link(
                    url='/scrooge/api/v0.9/api-token-auth/',
                    action='post',
                    encoding='application/json',
                    fields=[
                        Field('username', required=True, location='form'),
                        Field('password', required=True, location='form'),
                    ],
                    description="Fetch your personal API key",
                ),
            },
            'pricingserviceusages': {
                'create': Link(
                    url='/scrooge/api/v0.9/pricingserviceusages/',
                    action='post',
                    encoding='application/json',
                    fields=[
                        Field(
                            'pricing_service',
                            required=True,
                            location='form'
                        ),
                        Field('date', required=True, location='form'),
                        Field('overwrite', location='form'),
                        Field(
                            'ignore_unknown_services',
                            location='form',
                            type='boolean',
                        ),
                        Field(
                            'usages',
                            required=True,
                            location='form',
                            type='array',  # XXX
                        ),
                    ],
                    description=(
                        "Upload usages for given pricing service and date"
                    ),
                ),
                'read': Link(
                    url='/scrooge/api/v0.9/pricingserviceusages/{pricing_service_id}/{usages_date}/',  # noqa: E501
                    action='get',
                    fields=[
                        Field(
                            'pricing_service_id',
                            required=True,
                            location='path'
                        ),
                        Field('usages_date', required=True, location='path')
                    ],
                    description=(
                        "Fetch previously uploaded usages for given pricing "
                        "service and date"
                    ),
                ),
            },
            'teamtimedivision': {
                'create': Link(
                    url='/scrooge/api/v0.9/teamtimedivision/{team_id}/{year}/{month}/',  # noqa: E501
                    action='post',
                    encoding='application/json',
                    fields=[
                        Field('team_id', required=True, location='path'),
                        Field('year', required=True, location='path'),
                        Field('month', required=True, location='path'),
                        Field(
                            'division',
                            required=True,
                            location='form',
                            type='array'
                        ),  # XXX how to express objects here..?
                    ],
                    description=(
                        "Allocate team's working time (and therefore costs) "
                        "to some services"
                    ),
                ),
                'read': Link(
                    url='/scrooge/api/v0.9/teamtimedivision/{team_id}/{year}/{month}/',  # noqa: E501
                    action='get',
                    fields=[
                        Field('team_id', required=True, location='path'),
                        Field('year', required=True, location='path'),
                        Field('month', required=True, location='path')
                    ],
                    description=(
                        "Fetch time divisions uploaded for given team and "
                        "month"
                    ),
                ),
            },
        },
    }
)


@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "schema.json"))
    codec = OpenAPICodec()
    with open(filepath, 'r') as f:
        schema = codec.load(f.read())
    import ipdb; ipdb.set_trace()
    return response.Response(schema)



# XXX

generator = schemas.SchemaGenerator(title='Scrooge API 2')

@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_explicit_view(request):
    schema = generator.get_schema(request)
    return response.Response(schema)
