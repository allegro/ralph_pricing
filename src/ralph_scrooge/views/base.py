# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ralph.account.models import Perm, ralph_permission
from ralph.ui.views.common import MenuMixin

from ralph_scrooge.app import Scrooge as app


class Base(MenuMixin, TemplateView):
    module_name = app.module_name
    perms = [
        {
            'perm': Perm.has_scrooge_access,
            'msg': _("You don't have permission to access Scrooge."),
        },
    ]

    @ralph_permission(perms)
    def dispatch(self, *args, **kwargs):
        return super(Base, self).dispatch(*args, **kwargs)
