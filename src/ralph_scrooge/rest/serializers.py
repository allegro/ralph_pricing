# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import serializers


class MonthlyCostsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    forecast = serializers.BooleanField(default=False)
