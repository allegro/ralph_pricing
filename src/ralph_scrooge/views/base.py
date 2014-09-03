# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ralph.account.models import Perm, ralph_permission
from ralph.ui.views.common import MenuMixin

from ralph_scrooge import VERSION
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

    def get_context_data(self, **kwargs):
        context = super(Base, self).get_context_data(**kwargs)
        footer_items = []
        if self.request.user.is_staff:
            footer_items.append(
                MenuItem(
                    'Admin',
                    fugue_icon='fugue-toolbox',
                    href='/admin/ralph_scrooge',
                ),
            )
        footer_items.append(
            MenuItem(
                'logout',
                fugue_icon='fugue-door-open-out',
                pull_right=True,
                href=settings.LOGOUT_URL,
            )
        )
        footer_items.append(
            MenuItem(
                'Ralph',
                fugue_icon='fugue-home',
                href=reverse('search'),
            )
        )
        footer_items.append(
            MenuItem(
                "Version %s" % '.'.join((str(part) for part in VERSION)),
                fugue_icon='fugue-document-number',
            )
        )

        context.update({
            'mainmenu_items': MAIN_MENU,
            'footer_items': footer_items,
            'home_url': reverse('home'),
        })
        return context
