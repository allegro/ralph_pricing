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
from rest_framework.response import Response
from rest_framework.views import APIView

from ralph_scrooge.models import (
    DailyPricingObject,
    PricingObjectType,
)


class ComponentsContent(APIView):
    """
    A view that returns the contents for 'components' tables.
    """

    default_model = 'ralph_scrooge.models.DailyPricingObject'

    def get_types(self):
        """
        Returns Pricing Object Types defined in COMPONENTS_TABLE_SCHEMA.
        """
        return PricingObjectType.objects.filter(
            name__in=settings.COMPONENTS_TABLE_SCHEMA.keys()
        )

    def get_daily_pricing_objects(
            self, year, month, day, service, env=None, **kwargs
    ):
        """
        Returns Daily Pricing Objects related with passed service (and
        optionally environment) for a given date.
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

    def get_field(self, model, path):
        """
        Returns field of model with specified path, separeted by dot.
        If field does not exist, None is returned.

        Example:
        >> self.get_field(
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
                field = self.get_field(field, '.'.join(splited_cell[1:]))
        return field

    def get_headers(self, model, fields, prefix=''):
        """
        Returns components table schema headers.
        """
        ui_schema = []
        for field_path in fields:
            # if field_path is list or tuple,
            # then second element is column header
            if isinstance(field_path, (tuple, list)):
                ui_schema.append(field_path[1])
            else:
                if prefix:
                    field_path = '.'.join((prefix, field_path))
                field = self.get_field(model, field_path)
                if field:
                    ui_schema.append(field.verbose_name.title())
                else:
                    ui_schema.append(field_path)
        return dict(map(lambda x: (str(x[0]), x[1]), enumerate(ui_schema)))

    def process_schema(self, schema):
        """
        Analyzes the schema creating field list and header list
        """
        # get pricing object (sub)model
        app_label, _models, model_name = schema.get(
            'model',
            self.default_model,
        ).split('.')
        model = get_model(app_label, model_name)
        # parse headers according to 'fields' list in COMPONENTS_TABLE_SCHEMA
        # for this type
        headers = self.get_headers(
            model,
            schema['fields'],
        )
        # replace . with __ to get fields values from Django ORM
        django_fields = []
        for field in schema['fields']:
            # if field is list/tuple, first element is path, second is header
            if isinstance(field, (tuple, list)):
                field = field[0]
            django_fields.append(field.replace('.', '__'))
        return django_fields, headers

    def process_single_type(self, single_type, daily_pricing_objects):
        """
        Processing of single Pricing Object Type - returns information about
        single pricing object type component.
        """
        values = []
        # single type name must be in COMPONENTS_TABLE_SCHEMA in regular flow
        # (function called from components_content)
        django_fields, headers = self.process_schema(
            settings.COMPONENTS_TABLE_SCHEMA[single_type.name]
        )
        for dpo in daily_pricing_objects.filter(
            pricing_object__type=single_type,
        ).values_list(*django_fields):
            value = {str(x[0]): x[1] for x in enumerate(dpo)}
            values.append(value)
        return {
            "name": single_type.name,
            "icon_class": single_type.icon_class,
            "slug": slugify(single_type.name),
            "value": values,
            "schema": headers,
            "color": single_type.color,
        }

    def get(self, request, *args, **kwargs):
        daily_pricing_objects = self.get_daily_pricing_objects(*args, **kwargs)
        results = []
        for single_type in self.get_types():
            results.append(self.process_single_type(
                single_type, daily_pricing_objects
            ))
        return Response(results if results else [])
