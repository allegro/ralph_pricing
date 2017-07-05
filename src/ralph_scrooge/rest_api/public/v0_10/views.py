# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import django_filters
from rest_framework import filters, viewsets

from ralph_scrooge.models import (
    DailyUsage,
    PricingService,
    ServiceEnvironment,
    UsageType
)
from ralph_scrooge.rest_api.public.v0_10.pagination import (
    ScroogeLimitOffsetPagination
)
from ralph_scrooge.rest_api.public.v0_10.serializers import (
    DailyUsageSerializer,
    PricingServiceSerializer,
    UsageTypeSerializer,
)


class UsageTypesViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UsageTypeSerializer
    queryset = UsageType.objects.all().order_by('name').prefetch_related(
        'usageprice_set'
    )
    lookup_field = 'symbol'
    lookup_value_regex = '[^/]+'


class PricingServicesViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = PricingServiceSerializer
    queryset = PricingService.objects.all().order_by('name').prefetch_related(
        'usage_types'
    )
    lookup_field = 'symbol'
    lookup_value_regex = '[^/]+'


class DailyUsageFilter(django_filters.FilterSet):
    service_uid = django_filters.MethodFilter()

    def filter_service_uid(self, queryset, value):
        service_envs = ServiceEnvironment.objects.filter(service__ci_uid=value)
        return queryset.filter(service_environment__in=service_envs)

    class Meta:
        model = DailyUsage
        fields = {
            'date': ['exact', 'gte', 'lte', 'gt', 'lt'],
        }


class DailyUsageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyUsage.objects.select_related(
        'type',
        'service_environment__service',
        'service_environment__environment'
    )
    serializer_class = DailyUsageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DailyUsageFilter
    pagination_class = ScroogeLimitOffsetPagination
