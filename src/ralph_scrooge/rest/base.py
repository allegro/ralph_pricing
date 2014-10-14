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

from ralph.util.views import jsonify
from ralph_scrooge.models import (
    ServiceEnvironment,
    Team,
)


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

    start = date(2014, 9, 1)
    end = date.today() - timedelta(days=1)
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
        "service": {"current": False, "change": False},
        "env": {"current": False, "change": False},
        "year": {"current": False, "change": date_generated[-1].year},
        "month": {
            "current": False,
            "change": date_generated[-1].strftime('%B'),
        },
        "day": {"current": False, "change": date_generated[-1].day},
    }

    menu = OrderedDict()
    for i, service_environment in enumerate(service_environments):
        if i <= 1:
            menuStats['service']['change'] = service_environment.service.name
            menuStats['env']['change'] = service_environment.environment.name
        if (service_environment.service.name not in menu):
            menu[service_environment.service.name] = {"envs": []}
        menu[service_environment.service.name]["envs"].append(
            {"env": service_environment.environment.name}
        )

    results['menus'] = OrderedDict()
    results['menus']['service'] = []
    for row in menu:
        results['menus']['service'].append(
            {"service": row, "value": menu[row]}
        )
    results['menus']['teams'] = []
    for row in Team.objects.all():
        results['menus']['teams'].append({"team": row.name, "value": {}})
    results['menuStats'] = menuStats
    results['dates'] = dates
    return results
