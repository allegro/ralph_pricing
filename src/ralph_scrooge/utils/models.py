# Soruce code from
# https://github.com/ambv/kitdjango/blob/master/src/lck/django/common/models.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.utils.cache import memoize

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now


EDITOR_TRACKABLE_MODEL = getattr(settings, 'EDITOR_TRACKABLE_MODEL', User)
DIRTY_MARK = object()


@memoize
def model_is_user(model):
    return model in (User, 'auth.User')


class Named(db.Model):
    """Describes an abstract model with a unique ``name`` field."""

    name = db.CharField(
        verbose_name=_("name"), max_length=75, unique=True, db_index=True
    )

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    class NonUnique(db.Model):
        """Describes an abstract model with a non-unique ``name`` field."""

        name = db.CharField(verbose_name=_("name"), max_length=75)

        class Meta:
            abstract = True

        def __unicode__(self):
            return self.name


# TODO change it, if django > 1.8
# https://github.com/allegro/ralph/blob/ng/src/ralph/lib/mixins/models.py#L34
class TimeTrackable(db.Model):
    """Describes an abstract model whose lifecycle is tracked by time. Includes
    a ``created`` field that is set automatically upon object creation,
    a ``modified`` field that is updated automatically upon calling ``save()``
    on the object whenever a **significant** change was done, and
    a ``cache_version`` integer field that is automatically incremeneted any
    time a **significant** change is done.
    By a **significant** change we mean any change outside of those internal
    ``created``, ``modified``, ``cache_version``, ``display_count``
    or ``last_active`` fields. Full list of ignored fields lies in
    ``TimeTrackable.insignificant_fields``.
    Note: for admin integration ``lck.django.common.admin.ModelAdmin`` is
    recommended over the vanilla ``ModelAdmin``. It adds the ``created`` and
    ``modified`` fields as filters on the side of the change list and those
    fields will be rendered as read-only on the change form."""

    insignificant_fields = {
        'cache_version', 'modified', 'modified_by', 'display_count',
        'last_active'
    }

    created = db.DateTimeField(verbose_name=_("date created"), default=now)
    modified = db.DateTimeField(verbose_name=_("last modified"), default=now)
    cache_version = db.PositiveIntegerField(
        verbose_name=_("cache version"), default=0, editable=False
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TimeTrackable, self).__init__(*args, **kwargs)
        self._update_field_state()

    def save(self, update_modified=True, *args, **kwargs):
        """Overrides save(). Adds the ``update_modified=True`` argument.
        If False, the ``modified`` field won't be updated even if there were
        **significant** changes to the model."""
        if self.significant_fields_updated:
            self.cache_version += 1
            if update_modified:
                self.modified = now()
        super(TimeTrackable, self).save(*args, **kwargs)
        self._update_field_state()

    def update_cache_version(self, force=False):
        """Updates the cache_version bypassing the ``save()`` mechanism, thus
        providing better performance and consistency. Unless forced by
        ``force=True``, the update happens only when a **significant** change
        was made on the object."""
        if force or self.significant_fields_updated:
            # we're not using save() to bypass signals etc.
            self.__class__.objects.filter(pk=self.pk).update(
                cache_version=db.F("cache_version") + 1
            )

    def _update_field_state(self):
        self._field_state = self._fields_as_dict()

    def _fields_as_dict(self):
        fields = []
        for f in self._meta.fields:
            _name = f.name
            if f.rel:
                _name += '_id'
            fields.append((_name, getattr(self, _name)))
        return dict(fields)

    @property
    def significant_fields_updated(self):
        """Returns True on significant changes to the model.
        By a **significant** change we mean any change outside of those
        internal
        ``created``, ``modified``, ``cache_version``, ``display_count``
        or ``last_active`` fields. Full list of ignored fields lies in
        ``TimeTrackable.insignificant_fields``."""
        return bool(set(self.dirty_fields.keys()) - self.insignificant_fields)

    @property
    def dirty_fields(self):
        """dirty_fields() -> {'field1': 'old_value1', 'field2': 'old_value2',..}
        Returns a dictionary of attributes that have changed on this object
        and are not yet saved. The values are original values present in the
        database at the moment of this object's creation/read/last save."""
        new_state = self._fields_as_dict()
        diff = []
        for k, v in self._field_state.iteritems():
            try:
                if v == new_state.get(k):
                    continue
            except (TypeError, ValueError):
                pass  # offset-naive and offset-aware datetimes, etc.
            if v is DIRTY_MARK:
                v = new_state.get(k)
            diff.append((k, v))
        return dict(diff)

    def mark_dirty(self, *fields):
        """Forces `fields` to be marked as dirty to make all machinery checking
        for dirty fields treat them accordingly."""
        _dirty_fields = self.dirty_fields
        for field in fields:
            if field in _dirty_fields:
                continue
            self._field_state[field] = DIRTY_MARK

    def mark_clean(self, *fields, **kwargs):
        """Removes the forced dirty marks from fields.
        Fields that would be considered dirty anyway stay that way, unless
        `force` is set to True. In that case a field is unmarked until another
        change on it happens."""
        force = kwargs.get('force', False)
        _dirty_fields = self.dirty_fields
        _current_state = self._fields_as_dict()
        for field in fields:
            if field not in _dirty_fields:
                continue
            if self._field_state[field] is DIRTY_MARK:
                self._field_state[field] = _dirty_fields[field]
            elif force:
                self._field_state[field] = _current_state[field]


class EditorTrackable(db.Model):
    """Describes objects authored by users of the application. In the admin,
    on object creation the ``created_by`` field is set according to the editor.
    Same goes for modifying an object and the ``modified_by`` field. Works best
    in integration with TimeTrackable.
    If you would rather link to your user profile instead of the user object
    directly, use the ``EDITOR_TRACKABLE_MODEL`` (the same
    ``"app_name.ModelClass"``syntax as ``AUTH_PROFILE_MODULE``) setting.
    Note: for automatic editor updates in admin,
    ``lck.django.common.admin.ModelAdmin`` **MUST** be used instead of the
    vanilla ``ModelAdmin``. As a bonus, the ``created_by`` and ``modified_by``
    fields will appear as filters on the side of the change list
    and those fields will be rendered as read-only on the change form."""
    created_by = db.ForeignKey(
        EDITOR_TRACKABLE_MODEL, verbose_name=_("created by"), null=True,
        blank=True, default=None, related_name='+', on_delete=db.SET_NULL,
        limit_choices_to={
            'is_staff' if model_is_user(EDITOR_TRACKABLE_MODEL)
            else 'user__is_staff': True
        }
    )
    modified_by = db.ForeignKey(
        EDITOR_TRACKABLE_MODEL, verbose_name=_("modified by"), null=True,
        blank=True, default=None, related_name='+', on_delete=db.SET_NULL,
        limit_choices_to={
            'is_staff' if model_is_user(EDITOR_TRACKABLE_MODEL)
            else 'user__is_staff': True
        }
    )

    class Meta:
        abstract = True

    def get_editor_from_request(self, request):
        """This has to be overriden if you're using a custom editor model.
        Both ``auth.User`` and ``AUTH_PROFILE_MODULE`` are automatically
        handled."""
        if model_is_user(EDITOR_TRACKABLE_MODEL):
            return request.user
        else:
            return request.user.get_profile()

    def pre_save_model(self, request, obj, form, change):
        """Internal method used by ``lck.django.common.ModelAdmin``."""
        if not change:
            if not obj.created_by:
                obj.created_by = self.get_editor_from_request(request)
        else:
            obj.modified_by = self.get_editor_from_request(request)
