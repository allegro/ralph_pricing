# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.views.generic import View
from pluggableapp import PluggableApp
from rest_framework.viewsets import ViewSetMixin

from ralph.account.models import Perm
from ralph.ui.tests.functional.tests_view import LoginRedirectTest
from ralph_scrooge import urls
from ralph_scrooge.views.base import Base
from ralph_scrooge.views.bootstrapangular import BootstrapAngular


class TestPermissions(TestCase):
    def setUp(self):
        pass

    def test_urls(self):
        """
        Checks if every view from urls is subclass of Base view
        """
        for i in urls.__dict__.values():
            if (
                inspect.isclass(i) and
                issubclass(i, View) and
                not issubclass(i, (BootstrapAngular, ViewSetMixin))
            ):
                self.assertTrue(issubclass(i, Base))


class LoginRedirectTest(LoginRedirectTest):

    def test_hierarchy(self):
        """
        user with scrooge perms -> show scrooge
        user with core perms -> show core
        """
        hierarchy_data = [
            (Perm.has_scrooge_access,
             PluggableApp.apps['ralph_scrooge'].home_url),
            (Perm.has_core_access, reverse('search', args=('info', ''))),
        ]

        self.check_redirection(hierarchy_data)
