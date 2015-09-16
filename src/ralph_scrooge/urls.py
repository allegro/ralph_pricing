# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import include, patterns, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from rest_framework import routers
from tastypie.api import Api

from ralph_scrooge.api import PricingServiceUsageResource, SyncStatusViewSet
from ralph_scrooge.views.bootstrapangular import BootstrapAngular
from ralph_scrooge.views.collect_plugins import CollectPlugins
from ralph_scrooge.views.monthly_costs import MonthlyCosts
from ralph_scrooge.views.report_services_changes import ServicesChangesReportView  # noqa
from ralph_scrooge.views.report_services_costs import ServicesCostsReportView
from ralph_scrooge.views.report_services_usages import ServicesUsagesReportView  # noqa
from ralph_scrooge.rest import left_menu

from ralph_scrooge.utils.security import scrooge_permission

admin.autodiscover()

v09_api = Api(api_name='v0.9')
for r in (PricingServiceUsageResource, ):
    v09_api.register(r())

v09_router = routers.DefaultRouter()
for r in (SyncStatusViewSet, ):
    v09_router.register(r.resource_name, r)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rest/', include('ralph_scrooge.rest.urls')),
    url(r'^leftmenu/(?P<menu_type>\S+)/$', login_required(left_menu)),
    url(r'^api/', include(v09_api.urls)),
    url(r'^api/', include(v09_router.urls)),
    url(
        r'^$',
        login_required(BootstrapAngular.as_view()),
        name='services_costs_report',
    ),
    # OLD URLS
    url(
        r'^services-costs-report/$',
        scrooge_permission(ServicesCostsReportView.as_view()),
        name='services_costs_report',
    ),
    url(
        r'^services-usages-report/$',
        scrooge_permission(ServicesUsagesReportView.as_view()),
        name='services_usages_report',
    ),
    url(
        r'^services-changes-report/$',
        scrooge_permission(ServicesChangesReportView.as_view()),
        name='services_changes_report',
    ),
    url(
        r'^monthly-costs/$',
        scrooge_permission(MonthlyCosts.as_view()),
        name='monthly_costs',
    ),
    # other
    url(
        r'^collect-plugins/$',
        scrooge_permission(CollectPlugins.as_view()),
        name='collect_plugins',
    ),
)
