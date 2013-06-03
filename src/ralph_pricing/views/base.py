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


from ralph_pricing import VERSION


MAIN_MENU = [
    MenuItem(
        _("All ventures"),
        name='all-ventures',
        fugue_icon='fugue-store-medium',
        view_name='all_ventures',
    ),
    MenuItem(
        _("Top ventures"),
        name='top-ventures',
        fugue_icon='fugue-store',
        view_name='top_ventures',
    ),
    MenuItem(
        _("Devices"),
        name='devices',
        fugue_icon='fugue-wooden-box',
        view_name='devices',
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
]


class Base(TemplateView):
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
