# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import serializers

from ralph_scrooge.models import UsageType, UsagePrice, PricingService


class UsagePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsagePrice
        fields = ['price', 'forecast_price', 'start', 'end']


class UsageTypeSerializer(serializers.ModelSerializer):

    usage_price = UsagePriceSerializer(many=True, source='usageprice_set')

    class Meta:
        model = UsageType
        fields = ['id', 'name', 'symbol', 'usage_price', 'url']
        extra_kwargs = {
            'url': {
                'view_name': 'v0_10:usagetype-detail', 'lookup_field': 'symbol'
            }
        }


class SimpleUsageTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageType
        fields = ['id', 'name', 'symbol']


class PricingServiceSerializer(serializers.ModelSerializer):

    usage_types = SimpleUsageTypeSerializer(many=True)

    class Meta:
        model = PricingService
        fields = ['id', 'name', 'symbol', 'usage_types']
        extra_kwargs = {
            'url': {
                'view_name': 'v0_10:pricingservice-detail',
                'lookup_field': 'symbol'
            }
        }
