# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import include, patterns, url
from django.contrib.auth.decorators import login_required
from tastypie.api import Api

from ralph_scrooge.api import ServiceUsageResource
from ralph_scrooge.views.devices import Devices
from ralph_scrooge.views.extra_costs import ExtraCosts
from ralph_scrooge.views.home import Home
from ralph_scrooge.views.usages import Usages
from ralph_scrooge.views.statement import Statements
from ralph_scrooge.views.teams import Teams
from ralph_scrooge.views.teams_percent import TeamsPercent
from ralph_scrooge.views.report_services import ServicesReport
from ralph_scrooge.views.ventures_changes import VenturesChanges
from ralph_scrooge.views.ventures_daily_usages import VenturesDailyUsages

v09_api = Api(api_name='v0.9')
for r in (ServiceUsageResource, ):
    v09_api.register(r())

urlpatterns = patterns(
    '',
    url(r'^api/', include(v09_api.urls)),
    url(r'^$', login_required(Home.as_view()), name='home'),
    url(
        r'^extra-costs/$',
        login_required(ExtraCosts.as_view()),
        name='extra_costs',
        kwargs={'venture': None},
    ),
    url(
        r'^extra-costs/(?P<extra_cost>\d+)/$',
        login_required(ExtraCosts.as_view()),
        name='extra_costs',
    ),
    url(
        r'^usages/$',
        login_required(Usages.as_view()),
        name='usages',
        kwargs={'usage': None},
    ),
    url(
        r'^usages/(?P<usage>[^/]+)/$',
        login_required(Usages.as_view()),
        name='usages',
        kwargs={'type': 'price'},
    ),
    url(
        r'^teams/$',
        login_required(Teams.as_view()),
        name='teams',
        kwargs={'team': None, 'daterange': None},
    ),
    url(
        r'^teams/(?P<team>[^/]+)/$',
        login_required(Teams.as_view()),
        name='teams',
        kwargs={'daterange': None},
    ),
    url(
        r'^teams/(?P<team>[^/]+)/(?P<daterange>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
    ),
    url(
        r'^services-report/$',
        login_required(ServicesReport.as_view()),
        name='all_ventures',
    ),
    url(
        r'^ventures-daily-usages-report/$',
        login_required(VenturesDailyUsages.as_view()),
        name='ventures_daily_usages',
    ),
    url(
        r'^ventures-changes/$',
        login_required(VenturesChanges.as_view()),
        name='ventures_changes',
    ),
    url(
        r'^devices/$',
        login_required(Devices.as_view()),
        name='devices',
    ),
    url(
        r'^devices/(?P<venture>\d+)/$',
        login_required(Devices.as_view()),
        name='devices',
    ),
    url(
        r'^statement/$',
        login_required(Statements.as_view()),
        name='statement',
    ),
    url(
        r'^statement/(?P<statement_id>\d+)/$',
        login_required(Statements.as_view()),
        name='statement',
    ),
)
