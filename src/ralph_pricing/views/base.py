# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from bob.menu import MenuItem
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ralph.account.models import Perm, ralph_permission

from ralph_pricing import VERSION


MAIN_MENU = [
    MenuItem(
        _("Ventures report"),
        name='all-ventures',
        fugue_icon='fugue-store-medium',
        view_name='all_ventures',
    ),
    MenuItem(
        _("Devices report"),
        name='devices',
        fugue_icon='fugue-wooden-box',
        view_name='devices',
    ),
    MenuItem(
        _("Ventures daily usages"),
        name='ventures-daily-usages',
        fugue_icon='fugue-calendar-day',
        view_name='ventures_daily_usages',
    ),
    MenuItem(
        _("Devices ventures changes"),
        name='ventures-changes',
        fugue_icon='fugue-arrow-switch',
        view_name='ventures_changes',
    ),
    MenuItem(
        _("Extra costs"),
        name='extra-costs',
        fugue_icon='fugue-money-coin',
        view_name='extra_costs',
    ),
    MenuItem(
        _("Usage types"),
        name='usages',
        fugue_icon='fugue-beaker',
        view_name='usages',
    ),
    MenuItem(
        _("Teams"),
        name='teams',
        fugue_icon='fugue-users',
        view_name='teams',
    ),
    MenuItem(
        _("Statements"),
        name='statement',
        fugue_icon='fugue-clock-history',
        view_name='statement',
    ),
]


class Base(TemplateView):
    perms = [
        {
            'perm': Perm.has_scrooge_access,
            'msg': _("You don't have permission to see Scrooge."),
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
                    href='/admin/ralph_pricing',
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
