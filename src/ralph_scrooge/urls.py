# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import admin
from django.conf.urls.defaults import include, patterns, url
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken import views

import ralph_scrooge.plugins.subscribers  # noqa: F401
from ralph_scrooge.rest.pricing_service_usages import (
    create_pricing_service_usages,
    list_pricing_service_usages,
)
from ralph_scrooge.views.bootstrapangular import (
    BootstrapAngular,
    BootstrapAngular2
)

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api-token-auth/', views.obtain_auth_token),

    # TODO(xor-xor): These two URLs below are intentionally added here (instead
    # of ralph_scrooge.rest.urls) to provide backward compatibility with old,
    # TastyPie-based API.
    # TODO(xor-xor): Add some permission handling mechanism here once we
    # separate Scrooge from Ralph.
    url(
        r'^api/v0.9/pricingserviceusages/?$',
        create_pricing_service_usages,
        name='create_pricing_service_usages'
    ),
    url(
        r'^api/v0.9/pricingserviceusages/(?P<pricing_service_id>\d+)/(?P<usages_date>\d{4}-\d{2}-\d{2})/$',  # noqa
        list_pricing_service_usages,
        name='list_pricing_service_usages'
    ),

    url(r'^rest/', include('ralph_scrooge.rest.urls')),
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
    url(
        r'^login/', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}
    ),
    url(r'^logout/', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)


# TODO(xor-xor): Uncomment patterns for hermes below once Scrooge will be
# completely separated from Ralph. And remember, that endpoint for
# refreshVipEvent subscription will change from:
# /hermes/events/refreshVipEvent/
# to:
# /scrooge/hermes/events/refreshVipEvent/.
#
# urlpatterns += patterns(
#     '',
#     url(r'^hermes/', include('pyhermes.apps.django.urls'))
# )
