# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import viewsets, serializers

from ralph_scrooge.models import UsageType


class UsageTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageType
        fields = ['id', 'name']


class UsageTypesViewSet(viewsets.ModelViewSet):

    serializer_class = UsageTypeSerializer
    queryset = UsageType.objects.all().order_by('name')
