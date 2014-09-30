# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from bob.menu import MenuItem

# from ralph.account.models import Perm
from ralph.menu import Menu


class PricingMenu(Menu):
    module = MenuItem(
        'Pricing',
        name='ralph_pricing',
        fugue_icon='fugue-money-coin',
        href='/pricing/',
    )

    def get_submodules(self):
        return [
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

    def get_sidebar_items(self):
        return {}

menu_class = PricingMenu
