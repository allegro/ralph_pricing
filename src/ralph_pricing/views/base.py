#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.conf import settings
from django.views.generic import TemplateView
from bob.menu import MenuItem


MAIN_MENU = [
    MenuItem(
        'Ventures',
        name='ventures',
        fugue_icon='fugue-store',
        href='/pricing/ventures/',
    ),
    MenuItem(
        'Devices',
        name='devices',
        fugue_icon='fugue-wooden-box',
        href='/pricing/devices/',
    ),
    MenuItem(
        'Extra costs',
        name='extra-costs',
        fugue_icon='fugue-money-coin',
        href='/pricing/extra-costs/',
    ),
    MenuItem(
        'Usages',
        name='usages',
        fugue_icon='fugue-beaker',
        href='/pricing/usages/',
    ),
]


class Base(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(Base, self).get_context_data(**kwargs)
        footer_items = []
        if self.request.user.is_staff:
            footer_items.append(
                MenuItem('Admin', fugue_icon='fugue-toolbox', href='/admin'))
        footer_items.append(
            MenuItem(
                'logout',
                fugue_icon='fugue-door-open-out',
                pull_right=True,
                href=settings.LOGOUT_URL,
            )
        )

        context.update({
            'mainmenu_items': MAIN_MENU,
            'footer_items': footer_items,
        })
        return context



