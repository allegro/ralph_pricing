# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class MenuItem(object):
    """
    A container object for all the information about a single menu item.
    :param label: The label to be displayed for this menu item. Required.
    :param name: The symbolic name used in class names, ids and selections.
        If not specified, it is generated from the :attr:`label`.
    :param subitems: The list of :class:`MenuItem` instances for nested
        menus in :func:`bob.templatetags.bob.sidebar_menu` .
    :param href: The URL to which this menu item should link.
    :param view_name: The name of the URL rule to which this item should link.
    :param view_args: The positional arguments for the URL rule.
    :param view_kwargs: The keyword arguments for the URL rule.
    :param icon: A Bootstrap icon to show for this item.
    :param fugue_icon: A Fugue icon to show for this item, if available.
    :param collapsible: Whether the submenu should be collapsible.
        Default ``False``.
    :param collapsed: Whether the submenu should start collapsed.
        Default ``False``.
    :param indent: A string by which the item should be indented.
    """

    item_kind = 'link'

    def __init__(self, label, name=None, subitems=None, **kwargs):
        """
        """
        self.label = label
        if name is None:
            self.name = label.lower()
        else:
            self.name = name
        self.subitems = subitems
        self.kwargs = kwargs

    def get_href(self):
        href = self.kwargs.get('href')
        if href:
            return href
        view_name = self.kwargs.get('view_name')
        view_args = self.kwargs.get('view_args', [])
        view_kwargs = self.kwargs.get('view_kwargs', {})
        if view_name:
            return reverse(view_name, args=view_args, kwargs=view_kwargs)
        return ''


class Menu(object):
    module = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs
        # profile = self.request.user.get_profile()
        # self.has_perm = profile.has_perm

    def generate_menu_items(self, data):
        return [MenuItem(**t) for t in data]

    def get_module(self):
        if not self.module:
            raise ImproperlyConfigured(
                'Menu required definition of \'module\' or an implementation '
                'of \'get_module()\'')

        if not isinstance(self.module, MenuItem):
            raise ImproperlyConfigured(
                'Module must inheritence from \'MenuItem\'')

        return self.module

    def get_active_submodule(self):
        if not self.submodule:
            raise ImproperlyConfigured(
                'Menu required definition of \'submodule\' or an '
                'implementation of \'get_active_submodule()\'')

        if not isinstance(self.submodule, MenuItem):
            raise ImproperlyConfigured(
                'submodule must inheritence from \'MenuItem\'')

        return self.submodule

    def get_submodules(self):
        return []

    def get_sidebar_items(self):
        return {}


class ScroogeMenu(Menu):
    module = MenuItem(
        'Scrooge',
        name='ralph_scrooge',
        fugue_icon='fugue-money-coin',
        href='/',
    )

    def get_submodules(self):
        return [
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
                name='costs-calculation',
                fugue_icon='fugue-money-bag',
                view_name='costs_calculation',
            ),
        ]

    def get_sidebar_items(self):
        return {}

menu_class = ScroogeMenu
