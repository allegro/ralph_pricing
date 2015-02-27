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
    CostContent,
)

from ralph_scrooge.rest.menu import SubMenu
from ralph_scrooge.utils.security import (
    scrooge_permission,
    service_permission,
    team_permission,
)

urlpatterns = patterns(
    '',
    url(
        r'^cost/(?P<service>\d+)/(?P<env>\d+)/(?P<start>(\d\d-\d\d-\d\d\d\d))/(?P<end>(\d\d-\d\d-\d\d\d\d))/?$',
        scrooge_permission(CostContent.as_view()),
    ),
    url(
        r'^allocationadmin/(?P<year>\d+)/(?P<month>\d+)/?$',
        scrooge_permission(AllocationAdminContent.as_view()),
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
        r'^costcard/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',  # noqa
        service_permission(CostCardContent.as_view()),
    ),
    url(
        r'^submenu/?$',
        login_required(SubMenu.as_view()),
        name='submenu'
    ),
)
