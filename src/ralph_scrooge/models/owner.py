# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models as db
from django.db.utils import DatabaseError
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.utils.models import TimeTrackable
from dj.choices import Choices, Country, Gender
from tastypie.models import create_api_key


class UserProfile(db.Model):

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        db_table = 'account_profile'
        app_label = 'ralph_scrooge'

    user = db.OneToOneField(User)
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


class OwnershipType(Choices):
    _ = Choices.Choice

    technical = _("Technical owner")
    business = _("Business owner")


class OwnerManager(db.Manager):
    def get_query_set(self):
        return super(OwnerManager, self).get_query_set().select_related(
            'profile',
            'profile__user'
        )


class Owner(TimeTrackable):
    objects = OwnerManager()
    objects_raw = db.Manager()

    profile = db.OneToOneField(
        UserProfile,
        verbose_name=_("profile"),
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['profile__nick']

    def __unicode__(self):
        return ' '.join([
            self.profile.user.first_name,
            self.profile.user.last_name
        ])


class ServiceOwnership(db.Model):
    service = db.ForeignKey(
        'Service',
        verbose_name=_("service"),
        null=False,
        blank=False,
    )
    owner = db.ForeignKey(
        Owner,
        verbose_name=_("owner"),
        null=False,
        blank=False,
    )
    type = db.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        choices=OwnershipType(),
        verbose_name=_("Type"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('owner', 'service', 'type')

    def __unicode__(self):
        return '{} / {}'.format(self.service, self.owner)


class TeamManager(db.Model):
    team = db.ForeignKey(
        'Team',
        verbose_name=_("team"),
        null=False,
        blank=False,
    )
    manager = db.ForeignKey(
        Owner,
        verbose_name=_("manager"),
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('manager', 'team')

    def __unicode__(self):
        return '{} / {}'.format(self.team, self.manager)


# Code from Ralph 2
# https://github.com/allegro/ralph/blob/develop/src/ralph/util/models.py#L25
# TODO Only for django-tastypie, if we use only DRF delete this.
def create_api_key_ignore_dberrors(*args, **kwargs):
    try:
        return create_api_key(*args, **kwargs)
    except DatabaseError:
        # no such table yet, first syncdb
        from django.db import transaction
        transaction.rollback_unless_managed()


db.signals.post_save.connect(create_api_key_ignore_dberrors, sender=User)
