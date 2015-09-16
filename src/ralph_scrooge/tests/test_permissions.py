# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect

from django.test import TestCase
from django.views.generic import View
from rest_framework.viewsets import ViewSetMixin

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
