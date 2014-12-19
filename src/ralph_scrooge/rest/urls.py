#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from ralph_scrooge.rest import (
    AllocationAdminContent,
    AllocationClientService,
    AllocationClientPerTeam,
    CostCardContent,
)

from ralph_scrooge.rest.menu import SubMenu


urlpatterns = patterns(
    '',
    url(
        r'^allocateadmin/(?P<year>\d+)/(?P<month>\d+)/$',
        login_required(AllocationAdminContent.as_view()),
    ),
    url(
        r'^allocateclient/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        login_required(AllocationClientService.as_view()),
    ),
    url(
        r'^allocateclient/(?P<team>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',
        login_required(AllocationClientPerTeam.as_view()),
    ),
    url(
        r'^allocateclient/service/(?P<allocate_type>\S+)/save/$',
        login_required(AllocationClientService.as_view()),
    ),
    url(
        r'^allocateclient/team/(?P<allocate_type>\S+)/save/$',
        login_required(AllocationClientPerTeam.as_view()),
    ),
    url(
        r'^costcard/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        login_required(CostCardContent.as_view()),
    ),
    url(
        r'^submenu/$',
        login_required(SubMenu.as_view()),
        name='submenu'
    ),
)
