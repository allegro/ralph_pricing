# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from bob.menu import MenuItem

scrooge_menu = [
    MenuItem(
        _("Components"),
        name='components',
        fugue_icon='fugue-arrow-switch',
        view_name='components',
        href="/#/components/"
    ),
    MenuItem(
        _("Cost card"),
        name='costcard',
        fugue_icon='fugue-arrow-switch',
        view_name='costcard',
        href="/#/costcard/"
    ),
    MenuItem(
        _("Components costs"),
        name='costs',
        fugue_icon='fugue-arrow-switch',
        view_name='costs',
        href="/#/costs/"
    ),
    MenuItem(
        _("Allocations"),
        name='components',
        fugue_icon='fugue-arrow-switch',
        view_name='components',
        href="/#/allocation/client/"
    ),
    MenuItem(
        _("Allocations admin"),
        name='components',
        fugue_icon='fugue-arrow-switch',
        view_name='components',
        href="/#/allocation/admin/"
    ),
    MenuItem(
        _("Costs report"),
        name='services-costs-report',
        fugue_icon='fugue-store-medium',
        view_name='services_costs_report',
    ),
    MenuItem(
        _("Usages report"),
        name='services-usages-report',
        fugue_icon='fugue-calendar-day',
        view_name='services_usages_report',
    ),
    MenuItem(
        _("Collect plugins"),
        name='collect-plugins',
        fugue_icon='fugue-calendar-day',
        view_name='collect_plugins',
    ),
    MenuItem(
        _("Services changes report"),
        name='services-changes-report',
        fugue_icon='fugue-arrow-switch',
        view_name='services_changes_report',
    ),
    MenuItem(
        _("Costs calculation"),
        name='monthly-costs',
        fugue_icon='fugue-money-bag',
        view_name='monthly_costs',
    )
]
