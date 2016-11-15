# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import operator
from django.db import models
from functools import reduce
from rest_framework import viewsets

from ralph_scrooge.models import UsageType
from ralph_scrooge.rest.v010.serializers import UsageTypeSerializer

from rest_framework.filters import BaseFilterBackend


class SymbolFilterBackend(BaseFilterBackend):
    """
    Filter queryset by symbols. Multiple symbols could be specified in url query:
    `<URL>?symbol=abc&symbol=def&symbol=123`.
    """
    def _handle_symbols_filter(self, queryset, symbols):
        query = []
        for symbol in symbols:
            query.append(models.Q(symbol=symbol))
        if query:
            queryset = queryset.filter(reduce(operator.or_, query))
        return queryset

    def filter_queryset(self, request, queryset, view):
        symbols = request.GET.getlist('symbol')
        queryset = self._handle_symbols_filter(queryset, symbols)
        return queryset


class UsageTypesViewSet(viewsets.ModelViewSet):

    serializer_class = UsageTypeSerializer
    queryset = UsageType.objects.all().order_by('name').prefetch_related(
        'usageprice_set'
    )
    filter_backends = viewsets.ModelViewSet.filter_backends + [
        SymbolFilterBackend
    ]
    lookup_field = 'symbol'
