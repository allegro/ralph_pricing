# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import include, patterns, url
from django.contrib.auth.decorators import login_required
from tastypie.api import Api

from ralph_scrooge.api import PricingServiceUsageResource
from ralph_scrooge.views import BootstrapAngular
from ralph_scrooge.rest import left_menu, components_content
from ralph_scrooge.views.collect_plugins import CollectPlugins
from ralph_scrooge.views.extra_costs import ExtraCosts
from ralph_scrooge.views.usage_types import UsageTypes
from ralph_scrooge.views.statement import Statements
from ralph_scrooge.views.teams_percent import TeamsPercent
from ralph_scrooge.views.monthly_costs import MonthlyCosts
from ralph_scrooge.views.report_services_changes import ServicesChangesReportView  # noqa
from ralph_scrooge.views.report_services_costs import ServicesCostsReportView
from ralph_scrooge.views.report_services_usages import ServicesUsagesReportView # noqa


v09_api = Api(api_name='v0.9')
for r in (PricingServiceUsageResource, ):
    v09_api.register(r())

urlpatterns = patterns(
    '',
    url(
        r'^components/(?P<service>\S.+)/(?P<env>\S.+)/(?P<year>\d.+)/(?P<month>\S.+)/(?P<day>\d+)/$', # noqa
        components_content,
    ),
    url(r'^leftmenu/(?P<menu_type>\S.+)/$', left_menu),
    url(r'^api/', include(v09_api.urls)),
    url(
        r'^$',
        login_required(BootstrapAngular.as_view()),
        name='services_costs_report',
    ),
    url(
        r'^services-costs-report/$',
        login_required(ServicesCostsReportView.as_view()),
        name='services_costs_report',
    ),
    url(
        r'^services-usages-report/$',
        login_required(ServicesUsagesReportView.as_view()),
        name='services_usages_report',
    ),
    url(
        r'^services-changes-report/$',
        login_required(ServicesChangesReportView.as_view()),
        name='services_changes_report',
    ),
    url(
        r'^monthly-costs/$',
        login_required(MonthlyCosts.as_view()),
        name='monthly_costs',
    ),
    # costs forms
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
        r'^usage-types/$',
        login_required(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'usage_type_id': None},
    ),
    url(
        r'^usage-types/(?P<usage_type_id>[^/]+)/$',
        login_required(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'type': 'price'},
    ),
    url(
        r'^teams/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
        kwargs={'team': None, 'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
        kwargs={'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/(?P<daterange>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
    ),
    # statements
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
    # other
    url(
        r'^collect-plugins/$',
        login_required(CollectPlugins.as_view()),
        name='collect_plugins',
    ),
)
"""
    url(
        r'^services-costs-report/$',
        login_required(ServicesCostsReportView.as_view()),
        name='services_costs_report',
    ),
    url(
        r'^services-usages-report/$',
        login_required(ServicesUsagesReportView.as_view()),
        name='services_usages_report',
    ),
    url(
        r'^services-changes-report/$',
        login_required(ServicesChangesReportView.as_view()),
        name='services_changes_report',
    ),
    url(
        r'^monthly-costs/$',
        login_required(MonthlyCosts.as_view()),
        name='monthly_costs',
    ),
    # costs forms
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
        r'^usage-types/$',
        login_required(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'usage_type_id': None},
    ),
    url(
        r'^usage-types/(?P<usage_type_id>[^/]+)/$',
        login_required(UsageTypes.as_view()),
        name='usage_types',
        kwargs={'type': 'price'},
    ),
    url(
        r'^teams/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
        kwargs={'team': None, 'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
        kwargs={'daterange': None},
    ),
    url(
        r'^teams/(?P<team_id>[^/]+)/(?P<daterange>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
    ),
    # statements
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
    # other
    url(
        r'^collect-plugins/$',
        login_required(CollectPlugins.as_view()),
        name='collect_plugins',
    ),
)
"""
