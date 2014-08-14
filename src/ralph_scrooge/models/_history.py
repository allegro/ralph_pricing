#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from datetime import datetime

from django.db import models
from django.forms.models import model_to_dict
from simple_history.models import HistoricalRecords, transform_field

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now


class IntervalHistoricalRecords(HistoricalRecords):
    """
    Historical record with date intervals in which record was active.
    """
    def get_extra_fields(self, model, fields):
        """
        Add active from and active to fields to Historical Records
        """
        result = super(IntervalHistoricalRecords, self).get_extra_fields(
            model,
            fields,
        )
        result['active_from'] = models.DateTimeField(default=now)
        result['active_to'] = models.DateTimeField(default=datetime.max)
        result['__str__'] = lambda self: '%s active from %s to %s' % (
            self.history_object,
            self.active_from,
            self.active_to,
        )
        return result

    def copy_fields(self, model):
        """
        Copy fields with foreign keys relations
        """
        fields = {}
        for field in model._meta.fields:
            field = copy.copy(field)
            field.rel = copy.copy(field.rel)
            if isinstance(field, models.ForeignKey):
                field.rel.related_name = '+'
                field.attname = field.name
            transform_field(field)
            fields[field.name] = field
        return fields

    def _update_most_recent(self, manager, **fields):
        """
        Updates last historical record with passed fields values
        (ex. active_to)
        """
        try:
            # get last historical record
            most_recent = manager.all()[:1].get()
        except manager.model.DoesNotExist:
            return
        # update fields values
        for field, value in fields.items():
            setattr(most_recent, field, value)
        most_recent.save()

    def create_historical_record(self, instance, type):
        """
        Creates historical record (just original method)
        """
        current_now = now()
        history_date = getattr(instance, '_history_date', current_now)
        history_user = getattr(instance, '_history_user', None)
        active_from = current_now

        # update most recent history record
        manager = getattr(instance, self.manager_name)
        self._update_most_recent(manager, active_to=current_now)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        manager.create(
            history_date=history_date,
            history_type=type,
            history_user=history_user,
            active_from=active_from,
            **attrs
        )

    def post_delete(self, instance, **kwargs):
        """
        Updates most recent history record active to date
        """
        manager = getattr(instance, self.manager_name)
        self._update_most_recent(
            manager,
            active_to=now(),
            history_type='-'
        )


class ModelDiffMixin(object):
    """
    A model mixin that "tracks" model fields values and provide some useful api
    to know what fields have been changed.
    """

    class Meta:
        abstract = True
        app_label = 'ralph_scrooge'

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def _dict(self):
        return model_to_dict(
            self,
            fields=[field.name for field in self._meta.fields]
        )

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        # set skip_history_when_saving if historical record should not be saved
        # (historical record should be saved when instance is created or
        # modified (but only when some field value is changed))
        if self.pk and not self.has_changed:
            self.skip_history_when_saving = True
        try:
            super(ModelDiffMixin, self).save(*args, **kwargs)
        finally:
            if hasattr(self, 'skip_history_when_saving'):
                del self.skip_history_when_saving
        self.__initial = self._dict
