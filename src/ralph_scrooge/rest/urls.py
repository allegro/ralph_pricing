#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from ralph_scrooge.rest import (
    AcceptMonthlyCosts,
    AllocationAdminContent,
    AllocationClientService,
    AllocationClientPerTeam,
    CostCardContent,
    ComponentsContent,
    LeftMenuAPIView,
    ObjectCostsContent,
    MonthlyCosts,
    ServicesCostsReportContent,
    UsagesReportContent,
)
from ralph_scrooge.rest.router import urlpatterns as router_urlpatterns
from ralph_scrooge.rest.menu import SubMenu
from ralph_scrooge.utils.security import (
    superuser_permission,
    service_permission,
    team_permission,
)

urlpatterns = [
    url(r'^', include(router_urlpatterns)),  # TODO Permissions?
    url(
        r'^leftmenu/(?P<menu_type>\S+)/$',
        login_required(LeftMenuAPIView.as_view())
    ),
    url(
        r'^allocationadmin/(?P<year>\d+)/(?P<month>\d+)/?$',
        superuser_permission(AllocationAdminContent.as_view()),
    ),
    url(
        r'^allocationadmin/(?P<year>\d+)/(?P<month>\d+)/(?P<allocate_type>\S+)/save/?$',  # noqa
        superuser_permission(AllocationAdminContent.as_view()),
    ),
    url(
        r'^allocationclient/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',  # noqa
        service_permission(AllocationClientService.as_view()),
    ),
    url(
        r'^allocationclient/(?P<team>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',
        team_permission(AllocationClientPerTeam.as_view()),
    ),
    url(
        r'^allocationclient/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<allocate_type>\S+)/save/?$',  # noqa
        service_permission(AllocationClientService.as_view()),
    ),
    url(
        r'^allocationclient/(?P<team>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<allocate_type>\S+)/save/?$',  # noqa
        team_permission(AllocationClientPerTeam.as_view()),
    ),
    url(
        r'^components/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/?$',  # noqa
        service_permission(ComponentsContent.as_view()),
    ),
    url(
        r'^components/(?P<service>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/?$',  # noqa
        service_permission(ComponentsContent.as_view()),
    ),
    url(
        r'^costcard/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',  # noqa
        service_permission(CostCardContent.as_view()),
    ),
    url(
        r'^monthly_costs/?$',
        superuser_permission(MonthlyCosts.as_view()),
        name="monhtly-costs",
    ),
    url(
        r'^monthly_costs/(?P<job_id>[\w\-]+)?$',
        superuser_permission(MonthlyCosts.as_view()),
        name="monhtly-costs",
    ),
    url(
        r'^accept_monthly_costs/?$',
        superuser_permission(AcceptMonthlyCosts.as_view()),
        name="accept-monhtly-costs",
    ),
    url(
        r'^pricing_object_costs/(?P<service>\d+)/(?P<env>\d+)/(?P<start_date>[0-9-]+)/(?P<end_date>[0-9-]+)/?$',  # noqa
        service_permission(ObjectCostsContent.as_view()),
        name='pricing_object_costs'
    ),
    url(
        r'^submenu/?$',
        login_required(SubMenu.as_view()),
        name='submenu'
    ),
    url(
        r'^usages_report/?$',
        superuser_permission(UsagesReportContent.as_view()),
        name='usages_report_rest'
    ),
    url(
        r'^services_costs_report/?$',
        superuser_permission(ServicesCostsReportContent.as_view()),
        name='services_costs_report_rest'
    ),
]
