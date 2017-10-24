# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import serializers

from ralph_scrooge.models import (
    DailyUsage,
    PricingService,
    ServiceEnvironment,
    UsageType,
    UsagePrice
)


class UsagePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsagePrice
        fields = ['price', 'forecast_price', 'start', 'end']


class UsageTypeSerializer(serializers.ModelSerializer):

    usage_price = UsagePriceSerializer(many=True, source='usageprice_set')

    class Meta:
        model = UsageType
        fields = ['id', 'name', 'symbol', 'usage_price', 'url', 'support_team']
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


class ServiceEnvironmentSimpleSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source='service_name', read_only=True)
    environment = serializers.CharField(
        source='environment_name', read_only=True
    )
    service_uid = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceEnvironment
        fields = (
            'id', 'service', 'environment', 'service_uid',
        )


class DailyUsageSerializer(serializers.ModelSerializer):
    type = SimpleUsageTypeSerializer(read_only=True)
    service_environment = ServiceEnvironmentSimpleSerializer(read_only=True)

    class Meta:
        model = DailyUsage
        fields = [
            'id', 'date', 'type', 'service_environment', 'value', 'remarks'
        ]
