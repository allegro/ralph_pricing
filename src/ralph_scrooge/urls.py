# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from rest_framework.authtoken import views

import ralph_scrooge.plugins.subscribers  # noqa: F401
from ralph_scrooge import models as scrooge_models
from ralph_scrooge.rest_api.public.v0_9.pricing_service_usages import (
    create_pricing_service_usages,
    list_pricing_service_usages,
)
from ralph_scrooge.rest_api.public.swagger import BootstrapSwagger
from ralph_scrooge.rest_api.public.v0_10.service_environment_costs import (
    ServiceEnvironmentCosts,
)
from ralph_scrooge.rest_api.public.v0_10.router import (
    urlpatterns as router_v0_10_urlpatterns,
)
from ralph_scrooge.rest_api.public.v0_9.team_time_division import (
    TeamTimeDivision,
)
from ralph_scrooge.views.anomalies_ack import AnomaliesAck
from ralph_scrooge.views.autocomplete import ScroogeAutocomplete
from ralph_scrooge.views.bootstrapangular import (
    BootstrapAngular,
    BootstrapAngular2
)
from ralph_scrooge.utils.common import camel_case_to_kebab_case

admin.site.site_header = 'Scrooge'
admin.site.site_title = 'Scrooge'

admin.autodiscover()


autocomplete_urlpatterns = [
    url(
        '{}/$'.format(camel_case_to_kebab_case(model._meta.object_name)),
        login_required(
            ScroogeAutocomplete.as_view(
                model=model, search_fields=search_fields
            )
        ),
        name=camel_case_to_kebab_case(model._meta.object_name),
    )
    for model, search_fields in [
        (scrooge_models.ProfitCenter, ['name']),
        (scrooge_models.PricingService, ['name']),
        (scrooge_models.UsageType, ['name']),
        (
            scrooge_models.ScroogeUser,
            ['username', 'first_name', 'last_name']
        ),
        (
            scrooge_models.ServiceEnvironment,
            ['service__name', 'environment__name']
        ),
        (
            scrooge_models.PricingObjectModel,
            ['name', 'manufacturer', 'category']
        ),
        (scrooge_models.PricingObject, ['name']),
    ]
]

urlpatterns = [
    # Public REST API ---------------------------------------------------------

    # Swagger
    url(
        r'^scrooge/api/$',
        BootstrapSwagger.as_view(),
        name='swagger_view_scrooge_api',
    ),
    url(
        r'^api/$',
        RedirectView.as_view(pattern_name='swagger_view_scrooge_api'),
        name='swagger_view_api',
    ),

    # v0.10
    url(
        r'^scrooge/api/v0.10/',
        include(router_v0_10_urlpatterns, namespace='v0_10'),
    ),
    url(
        r'^scrooge/api/v0.10/service-environment-costs/$',
        ServiceEnvironmentCosts.as_view(),
        name='service_environment_costs',
    ),
    url(
        r'^scrooge/api/v0.10/api-token-auth/',
        views.obtain_auth_token,
    ),
    url(
        r'^scrooge/api/v0.10/team-time-division/(?P<team_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',  # noqa: E501
        TeamTimeDivision.as_view(),
        name='team_time_division_v10',
    ),
    url(
        r'^scrooge/api/v0.10/pricing-service-usages/?$',
        create_pricing_service_usages,
        name='create_pricing_service_usages_v10',
    ),
    url(
        r'^scrooge/api/v0.10/pricing-service-usages/(?P<pricing_service_id>\d+)/(?P<usages_date>\d{4}-\d{2}-\d{2})/$',  # noqa: E501
        list_pricing_service_usages,
        name='list_pricing_service_usages_v10',
    ),

    # v0.9 (endpoints in this hierarchy should be considered as deprecated)
    url(
        r'^scrooge/api/v0.9/api-token-auth/',
        views.obtain_auth_token,
    ),
    url(
        r'^scrooge/api/v0.9/teamtimedivision/(?P<team_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',  # noqa: E501
        TeamTimeDivision.as_view(),
        name='team_time_division',
    ),
    url(
        r'^scrooge/api/v0.9/pricingserviceusages/?$',
        create_pricing_service_usages,
        name='create_pricing_service_usages',
    ),
    url(
        r'^scrooge/api/v0.9/pricingserviceusages/(?P<pricing_service_id>\d+)/(?P<usages_date>\d{4}-\d{2}-\d{2})/$',  # noqa: E501
        list_pricing_service_usages,
        name='list_pricing_service_usages',
    ),

    # Internal REST API for GUI -----------------------------------------------
    url(r'^scrooge/rest/', include('ralph_scrooge.rest_api.private.urls')),


    # autocomplete
    url(
        r'^autocomplete/',
        include(autocomplete_urlpatterns, namespace='autocomplete'),
    ),

    # All the rest ------------------------------------------------------------
    url(
        r'^$',
        login_required(BootstrapAngular.as_view()),
        name='bootstrap_angular',
    ),
    url(
        r'^ui/$',
        login_required(BootstrapAngular2.as_view()),
        name='bootstrap_angular2',
    ),
    url(
        r'^login/', auth_views.login, {'template_name': 'admin/login.html'}
    ),
    url(r'^logout/', auth_views.logout, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hermes/', include('pyhermes.apps.django.urls')),
    url(
        r'^ack/(?P<ut_id>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/$',
        login_required(AnomaliesAck.as_view()),
        name='anomalies_ack',
    )
]
