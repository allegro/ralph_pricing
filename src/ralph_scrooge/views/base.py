# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView

from ralph_scrooge.menu import ScroogeMenu


class MenuMixin(object):
    module_name = None
    submodule_name = None
    sidebar_item_name = None

    def dispatch(self, request, *args, **kwargs):
        self.menus = [ScroogeMenu(request)]
        return super(MenuMixin, self).dispatch(request, *args, **kwargs)

    @property
    def current_menu(self):
        menu = None
        if hasattr(self, 'menus'):
            for menu in self.menus:
                if menu.module.name == self.module_name:
                    break
        return menu

    @property
    def active_module(self):
        if not self.module_name:
            raise ImproperlyConfigured(
                '{view} required definition of \'module_name\''.format(
                    view=self.__class__.__name__))
        return self.module_name

    @property
    def active_submodule(self):
        if not self.submodule_name:
            raise ImproperlyConfigured(
                '{view} required definition of \'submodule_name\''.format(
                    view=self.__class__))
        return self.submodule_name

    @property
    def active_sidebar_item(self):
        return self.sidebar_item_name

    def get_modules(self):
        if hasattr(self, 'menus'):
            main_menu = [menu.module for menu in self.menus]
        else:
            main_menu = []
        return main_menu

    def get_submodules(self):
        if self.current_menu:
            submodules = self.current_menu.get_submodules()
        else:
            submodules = None
        return submodules

    def get_context_data(self, **kwargs):
        context = super(MenuMixin, self).get_context_data(**kwargs)
        current_menu = self.current_menu
        if not current_menu:
            sidebar = None
        else:
            sidebar = current_menu.get_sidebar_items().get(
                self.active_submodule, None
            )
        context.update({
            'main_menu': self.get_modules(),
            'submodules': self.get_submodules(),
            'sidebar': sidebar,
            'active_menu': current_menu,
            'active_module': self.active_module,
            'active_submodule': self.active_submodule,
            'active_sidebar_item': self.active_sidebar_item,
        })
        return context


class Base(MenuMixin, TemplateView):
    module_name = 'ralph_scrooge'
