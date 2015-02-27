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
from ralph_scrooge.views.bootstrapangular import BootstrapAngular
from ralph_scrooge.views.collect_plugins import CollectPlugins
from ralph_scrooge.views.extra_costs import ExtraCosts
from ralph_scrooge.views.usage_types import UsageTypes
from ralph_scrooge.views.statement import Statements
from ralph_scrooge.views.teams_percent import TeamsPercent
from ralph_scrooge.views.monthly_costs import MonthlyCosts
from ralph_scrooge.views.report_services_changes import ServicesChangesReportView  # noqa
from ralph_scrooge.views.report_services_costs import ServicesCostsReportView
from ralph_scrooge.views.report_services_usages import ServicesUsagesReportView  # noqa
from ralph_scrooge.rest import left_menu

from ralph_scrooge.utils.security import scrooge_permission

v09_api = Api(api_name='v0.9')
for r in (PricingServiceUsageResource, ):
    v09_api.register(r())

v09_router = routers.DefaultRouter()
for r in (SyncStatusViewSet, ):
    v09_router.register(r.resource_name, r)

urlpatterns = patterns(
    '',
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
    # costs forms
    url(
        r'^extra-costs/$',
        scrooge_permission(ExtraCosts.as_view()),
        name='extra_costs',
        kwargs={'venture': None},
    ),
    url(
        r'^extra-costs/(?P<extra_cost>\d+)/$',
        scrooge_permission(ExtraCosts.as_view()),
        name='extra_costs',
    ),
    url(
        r'^usage-types/$',
        scrooge_permission(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'usage_type_id': None},
    ),
    url(
        r'^usage-types/(?P<usage_type_id>[^/]+)/$',
        scrooge_permission(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'type': 'price'},
    ),
    url(
        r'^teams/$',
        scrooge_permission(TeamsPercent.as_view()),
        name='teams',
        kwargs={'team': None, 'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/$',
        scrooge_permission(TeamsPercent.as_view()),
        name='teams',
        kwargs={'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/(?P<daterange>[^/]+)/$',
        scrooge_permission(TeamsPercent.as_view()),
        name='teams',
    ),
    # statements
    url(
        r'^statement/$',
        scrooge_permission(Statements.as_view()),
        name='statement',
    ),
    url(
        r'^statement/(?P<statement_id>\d+)/$',
        scrooge_permission(Statements.as_view()),
        name='statement',
    ),
    # other
    url(
        r'^collect-plugins/$',
        scrooge_permission(CollectPlugins.as_view()),
        name='collect_plugins',
    ),
)
