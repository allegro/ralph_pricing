# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import include, patterns, url
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from tastypie.api import Api

from ralph_scrooge.api import PricingServiceUsageResource, SyncStatusViewSet
from ralph_scrooge.views.bootstrapangular import (
    BootstrapAngular,
    BootstrapAngular2
)


v09_api = Api(api_name='v0.9')
for r in (PricingServiceUsageResource, ):
    v09_api.register(r())

v09_router = routers.DefaultRouter()
for r in (SyncStatusViewSet, ):
    v09_router.register(r.resource_name, r)

urlpatterns = patterns(
    '',
    url(r'^rest/', include('ralph_scrooge.rest.urls')),
    url(r'^api/', include(v09_api.urls)),
    url(r'^api/', include(v09_router.urls)),
    url(
        r'^$',
        login_required(BootstrapAngular.as_view()),
        name='services_costs_report',
    ),
    url(
        r'^ui/$',
        login_required(BootstrapAngular2.as_view()),
        name='angular2',
    ),
)
