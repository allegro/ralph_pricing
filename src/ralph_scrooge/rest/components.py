#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from django.conf import settings
from django.db.models import get_model
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ralph.util.views import jsonify
from ralph_scrooge.models import (
    DailyPricingObject,
    PricingObjectType,
)


def _get_types():
    """
    Returns Pricing Object Types defined in COMPONENTS_TABLE_SCHEMA.
    """
    return PricingObjectType.objects.filter(
        name__in=settings.COMPONENTS_TABLE_SCHEMA.keys()
    )


def _get_daily_pricing_objects(year, month, day, service, env=None, **kwargs):
    """
    Returns Daily Pricing Objects related with passed service (and optionally
    environment) for given date.
    """
    query = DailyPricingObject.objects.filter(
        service_environment__service__id=service,
        date=date(
            year=int(year),
            month=int(month),
            day=int(day),
        )
    ).select_related(
        "pricing_object",
    )
    if env:
        query = query.filter(service_environment__environment__id=env)
    return query


def _get_field(model, path):
    """
    Returns field of model with specified path, separeted by dot. If field does
    not exist, None is returned.

    Example:
    >> _get_field(
    ...    ralph_scroge.models.DailyPricingObject,
    ...    'pricing_object.service_environment.service.name'
    ...)
    <django.db.models.fields.CharField: name>
    """
    splited_cell = path.split('.')
    field = None
    try:
        field, _model, direct, m2m = model._meta.get_field_by_name(
            splited_cell[0]
        )
    except FieldDoesNotExist:
        pass
    else:
        # get appropriate field if it's relation
        if isinstance(field, RelatedField):
            field = field.rel.to
        elif isinstance(field, RelatedObject):
            field = field.model
        # call recursively if it wasn't last field on path
        if len(splited_cell) > 1:
            field = _get_field(field, '.'.join(splited_cell[1:]))
    return field


def _get_headers(model, fields, prefix=''):
    """
    Returns components table schema headers.
    """
    ui_schema = []
    for field_path in fields:
        if prefix:
            field_path = '.'.join((prefix, field_path))
        field = _get_field(model, field_path)
        if field:
            ui_schema.append(field.verbose_name.title())
        else:
            ui_schema.append(field_path)
    return dict(map(lambda x: (str(x[0]), x[1]), enumerate(ui_schema)))


def process_single_type(single_type, daily_pricing_objects):
    """
    Processing of single Pricing Object Type - returns information about
    single pricing object type component.
    """
    value = []
    # single type name must be in COMPONENTS_TABLE_SCHEMA in regular flow
    # (function called from components_content)
    schema = settings.COMPONENTS_TABLE_SCHEMA[single_type.name]
    # get pricing object (sub)model
    app_label, _models, model_name = schema.get(
        'model',
        'ralph_scrooge.models.DailyPricingObject'
    ).split('.')
    model = get_model(app_label, model_name)
    # parse headers according to 'fields' list in COMPONENTS_TABLE_SCHEMA
    # for this type
    headers = _get_headers(
        model,
        schema['fields'],
        prefix='pricing_object',
    )
    # replace . with __ to get fields values from Django ORM
    django_fields = ['__'.join((
        'pricing_object',
        f.replace('.', '__')
    )) for f in schema['fields']]

    for dpo in daily_pricing_objects.filter(
        pricing_object__type=single_type,
    ).values_list(*django_fields):
        value.append(dict(map(lambda x: (str(x[0]), x[1]), enumerate(dpo))))
    return {
        "name": single_type.name,
        "icon_class": single_type.icon_class,
        "slug": slugify(single_type.name),
        "value": value,
        "schema": headers,
        "color": single_type.color,
    }


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def components_content(request, *args, **kwargs):
    daily_pricing_objects = _get_daily_pricing_objects(*args, **kwargs)
    results = []
    for single_type in _get_types():
        results.append(process_single_type(single_type, daily_pricing_objects))
    return results if results else {}
