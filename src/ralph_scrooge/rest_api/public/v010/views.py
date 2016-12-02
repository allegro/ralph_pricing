# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework import viewsets

from ralph_scrooge.models import UsageType
from ralph_scrooge.rest_api.public.v010.serializers import UsageTypeSerializer


class UsageTypesViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UsageTypeSerializer
    queryset = UsageType.objects.all().order_by('name').prefetch_related(
        'usageprice_set'
    )
    lookup_field = 'symbol'
    lookup_value_regex = '[^/]+'
