# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from ralph_pricing.views.home import Home
from ralph_pricing.views.extra_costs import ExtraCosts


urlpatterns = patterns(
    '',
    url(r'^$', login_required(Home.as_view()), name='home'),
    url(
        r'^extra-costs/$',
        login_required(ExtraCosts.as_view()),
        name='extra-costs',
        kwargs={'venture': None},
    ),
    url(
        r'^extra-costs/(?P<venture>\d+)/$',
        login_required(ExtraCosts.as_view()),
        name='extra-costs',
    ),

)

