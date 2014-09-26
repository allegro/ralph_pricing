#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from time import strptime

from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta

from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ralph.util.views import jsonify
from ralph_scrooge.models import (
	ServiceEnvironment,
	DailyPricingObject,
	PricingObjectType,
)


def monthToNum(date):
	return{
	        'January' : 1,
	        'February' : 2,
	        'March' : 3,
	        'April' : 4,
	        'May' : 5,
	        'June' : 6,
	        'July' : 7,
	        'August' : 8,
	        'September' : 9,
	        'October' : 10,
	        'November' : 11,
	        'December' : 12
	}[date]

COMPONENTS_SCHEMA = {
	"Asset": ['Asset id', 'Name', 'Serial number', 'Barcode'],
}
@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def components_content(request, *args, **kwargs):
	daily_pricing_objects = DailyPricingObject.objects.filter(
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
	results = []
	for single_type in PricingObjectType():
		if single_type[1] == u'-' or single_type[1] == u'Unknown':
			continue
		value = []
		for daily_pricing_object in daily_pricing_objects.filter(
			pricing_object__type=single_type[0],
		):
			value.append([
				daily_pricing_object.pricing_object.id,
				daily_pricing_object.pricing_object.name,
			])
		results.append({
			"name": single_type[1],
			"schema": ['Id', 'Name'],
			"value": value,
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

	results =  {}

	start = date(2013, 01, 01)
	end = date(2015, 12, 01)
	date_generated = [start + timedelta(days=x) for x in range(
		0,
		(end - start).days + 1,
	)]
	dates =	OrderedDict()
	for one_day_date in date_generated:
		year = one_day_date.year
		month = one_day_date.strftime('%B')
		if not year in dates:
			dates[year] = OrderedDict()
		if not month in dates[year]:
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
		print (i)
		if i <= 1:
			menuStats['service']['change'] = service_environment.service.name
			menuStats['env']['change'] = service_environment.environment.name
		environments = []
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
	return results
