#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date, timedelta

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models.fields import FieldDoesNotExist

from ralph.util.views import jsonify
from ralph_scrooge.models import (
    ServiceEnvironment,
    DailyPricingObject,
    PricingObjectType,
    PricingObjectColor,
)


def monthToNum(date):
    return{
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }[date]


def _get_types():
    types = []
    for single_type in PricingObjectType():
        if single_type[1] not in settings.COMPONENTS_TABLE_SCHEMA:
            continue
        types.append(single_type)
    return types


def _get_daily_pricing_objects(*args, **kwargs):
    return DailyPricingObject.objects.filter(
        service_environment__service__name=kwargs.get(
            'service',
        ),
        service_environment__environment__name=kwargs.get(
            'env',
        ),
        date=date(
            year=int(kwargs.get('year')),
            month=monthToNum(kwargs.get('month')),
            day=int(kwargs.get('day')),
        )
    ).select_related(
        "pricing_object",
    )


def _get_field(model, cell):
    splited_cell = cell.split('.')
    name = value = False
    if len(splited_cell) > 1:
        field, value = _get_field(
            getattr(model, splited_cell[0]),
            ".".join(splited_cell[1:]),
        )
    else:
        try:
            field = model._meta.get_field_by_name(cell)
            value = getattr(model, cell)
        except FieldDoesNotExist:
            pass

    return (field, value)


def _get_fields(model, schema):
    ui_schema = {}
    fields = {}
    for cell in schema:
        results = _get_field(model, cell)
        if results:
            ui_schema[cell] = results[0][0].verbose_name.title()
            fields[results[0][0].verbose_name.title()] = results[1]
    return (fields, ui_schema)


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def components_content(request, *args, **kwargs):
    daily_pricing_objects = _get_daily_pricing_objects(*args, **kwargs)
    results = []
    for single_type in _get_types():
        value = []
        ui_schema = {}
        for daily_pricing_object in daily_pricing_objects.filter(
            pricing_object__type=single_type[0],
        ):
            fields = _get_fields(
                daily_pricing_object.pricing_object,
                settings.COMPONENTS_TABLE_SCHEMA[single_type[1]],
            )
            ui_schema.update(fields[1])
            value.append(fields[0])
        results.append({
            "name": single_type[1],
            "value": value,
            "schema": ui_schema,
            "color": PricingObjectColor.raw_from_id(single_type[0]),
        })
    return results if results else {}


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def left_menu(request, *args, **kwargs):
    service_environments = ServiceEnvironment.objects.all().select_related(
        "service",
        "environment",
    ).order_by(
        "service__name",
    )

    results = {}

    start = date(2013, 01, 01)
    end = date(2015, 12, 01)
    date_generated = [start + timedelta(days=x) for x in range(
        0,
        (end - start).days + 1,
    )]
    dates = OrderedDict()
    for one_day_date in date_generated:
        year = one_day_date.year
        month = one_day_date.strftime('%B')
        if year not in dates:
            dates[year] = OrderedDict()
        if month not in dates[year]:
            dates[year][month] = []
        dates[year][month].append(one_day_date.day)

    menuStats = {
        "service": {"current": False, "change": "Stock"},
        "env": {"current": False, "change": "prod"},
        "year": {"current": False, "change": "2014"},
        "month": {
            "current": False,
            "change": "September",
        },
        "day": {"current": False, "change": "25"},
    }
    """
    menuStats = {
        "service": {"current": False, "change": False},
        "env": {"current": False, "change": False},
        "year": {"current": False, "change": date_generated[-1].year},
        "month": {
            "current": False,
            "change": date_generated[-1].strftime('%B'),
        },
        "day": {"current": False, "change": date_generated[-1].day},
    }
    """
    menu = OrderedDict()
    for i, service_environment in enumerate(service_environments):
        #if i <= 1:
            # menuStats['service']['change'] = service_environment.service.name
            # menuStats['env']['change'] = service_environment.environment.name
        if (service_environment.service.name not in menu):
            menu[service_environment.service.name] = {"envs": []}
        menu[service_environment.service.name]["envs"].append(
            {"env": service_environment.environment.name}
        )

    results['menu'] = []
    for row in menu:
        results['menu'].append({"service": row, "value": menu[row]})
    results['menuStats'] = menuStats
    results['dates'] = dates
    import time
    time.sleep(3)

    return results
