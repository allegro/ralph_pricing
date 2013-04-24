# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_pricing.models import Venture

from django.views.generic import (
    TemplateView,
)
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


def ventures_menu(ventures=None):
    if ventures is None:
        ventures = Venture.objects.filter(parent=None)
    items = []
    for venture in ventures.order_by('name'):
        item = MenuItem(
            venture.name,
            fugue_icon='fugue-store-medium',
            indent = ' ',
            collapsed = True,
            collapsible = True,
        )
        item.subitems = ventures_menu(venture.children)
        items.append(item)
    return items


class Base(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(Base, self).get_context_data(**kwargs)
        context.update({
            'mainmenu_items': MAIN_MENU,
        })
        return context


class Home(Base):
    template_name = 'ralph_pricing/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context.update({
            'sidebar_items': ventures_menu(),
        })
        return context

