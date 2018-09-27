# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.models import CostDateStatus
from rest_framework import serializers


class MonthlyCostsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    forecast = serializers.BooleanField(default=False)


class CostInfoSerializer(serializers.Serializer):
    total_cost = serializers.DecimalField(decimal_places=2, max_digits=8)
    service_uid = serializers.CharField()
    environment = serializers.CharField()


class SyncAcceptedCostsSerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    type = serializers.CharField()
    costs = CostInfoSerializer(many=True)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if data['date_from'] > data['date_to']:
            raise serializers.ValidationError("date_to must occur after date_from")
        if self._check_accepted_costs(data['date_from'], data['date_to']):
            raise serializers.ValidationError(
                'Costs are already accepted between selected dates'
            )
        return data

    def _check_accepted_costs(self, date_from, date_to):
        return CostDateStatus.objects.filter(
            date__gte=date_from,
            date__lte=date_to,
            accepted=True
        ).exists()
