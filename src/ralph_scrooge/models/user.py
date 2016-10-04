# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from dj.choices import Country, Gender

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models as db


class ScroogeUser(AbstractUser):
    nick = db.CharField(
        verbose_name=_("visible nick"), blank=True, default='', max_length=30,
        help_text=_((
            "Fill this field if you wish to change "
            "your visible nick. You can use Unicode characters and spaces. "
            "Keep in mind that your original username (the one you use to "
            "log into the site) will remain unchanged."
        ))
    )
    birth_date = db.DateField(
        verbose_name=_("birth date"), blank=True, null=True
    )
    gender = db.PositiveIntegerField(
        verbose_name=_("gender"), choices=Gender(), default=Gender.male.id)
    country = db.PositiveIntegerField(
        verbose_name=_("country"), choices=Country(), default=Country.pl.id)
    city = db.CharField(verbose_name=_("city"), max_length=30, blank=True)

    activation_token = db.CharField(
        verbose_name=_("activation token"), max_length=40, editable=False,
        blank=True, default=''
    )

    company = db.CharField(max_length=64, blank=True)
    employee_id = db.CharField(max_length=64, blank=True)
    profit_center = db.CharField(max_length=1024, blank=True)
    cost_center = db.CharField(max_length=1024, blank=True)
    department = db.CharField(max_length=64, blank=True)
    manager = db.CharField(max_length=1024, blank=True)
    location = db.CharField(max_length=128, blank=True)
    segment = db.CharField(max_length=256, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'scrooge_user'
        app_label = 'ralph_scrooge'
