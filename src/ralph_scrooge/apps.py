# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ScroogeAppConfig(AppConfig):
    name = 'ralph_scrooge'
    verbose_name = _('Scrooge')
