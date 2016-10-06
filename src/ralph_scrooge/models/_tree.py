# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

from django.db import models as db
from django.db.models.base import ModelBase


class NamedtupleDjangoModelMeta(ModelBase):
    """
    Add namedtuple mapping for Django ORM model.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super(NamedtupleDjangoModelMeta, cls).__new__(
            cls, name, bases, attrs
        )
        # create namedtuple with fields from model
        # notice that ForeignKeys fields are inserted with '_id' suffix
        # (ex. user -> user_id)
        ntpl = namedtuple(
            name,
            ['pk'] + [f.attname for f in new_class._meta.fields]
        )
        # set defaults to None - this will allow to specify subset of fields
        # when creating new object
        ntpl.__new__.__defaults__ = (None,) * (len(ntpl._fields))
        # create set of fields to speed-up fields searching
        ntpl._fields_set = set(ntpl._fields)
        # mapping from foreign key name to it's database field name
        # (ex. user -> user_id)
        ntpl._foreign_key_mapping = {
            f.name: f.attname for f in new_class._meta.fields if (
                isinstance(f, db.ForeignKey)
            )
        }
        new_class.namedtuple = ntpl
        return new_class


class MultiPathNodeQuerySet(db.QuerySet):
    def _populate_pk_values(self, objs):
        # this requires _meta on single object which is missing for namedtuple
        pass


class MultiPathNode(db.Model):
    __metaclass__ = NamedtupleDjangoModelMeta
    _path_link = '/'
    _path_field = None

    path = db.CharField(max_length=255,)
    depth = db.PositiveIntegerField(default=0,)
    parent = None  # to be replaced in inheriting class

    class Meta:
        abstract = True
        app_label = 'ralph_scrooge'

    @classmethod
    def _parse_path(cls, parent_path, data):
        """
        Returns path as join of parent path with value of current object path
        field value.
        """
        path_field_value = data.get(cls._path_field)
        l = []
        if parent_path:
            l.append(parent_path)
        l.append(path_field_value)
        return cls._path_link.join(map(str, l))

    @classmethod
    def build_tree(cls, *args, **kwargs):
        result = cls._build_tree(*args, **kwargs)
        cls.objects.bulk_create(result)
        return result

    @classmethod
    def _are_params_valid(cls, params):
        return True

    @classmethod
    def _build_tree(cls, tree, parent=None, **global_params):
        """
        Build objects ready to save to DB using bulk_create according to tree
        list.

        :param list tree: list of dicts. dict values will be passed as kwargs
            to new objects. Dict '_children' list value will be used to create
            children nodes.

        :rtype: list of namedtuples
        """
        assert isinstance(tree, (list, tuple))
        result = []
        for child in tree:
            assert isinstance(child, dict)
            params = {}
            for k, v in child.items():
                # check if key is in foreignkey mapping - if yes, it's Foreign
                # Key - should take it mapped key as key (ex. user -> user_id)
                # and pk as value (ex. user -> user.id)
                if k in cls.namedtuple._foreign_key_mapping:
                    k = cls.namedtuple._foreign_key_mapping[k]
                    if v:
                        v = v.pk
                # save only params which are present in model
                if k in cls.namedtuple._fields_set:
                    params[k] = v
            params.update(global_params)
            if cls._are_params_valid(params):
                params['depth'] = parent.depth + 1 if parent else 0
                params['path'] = cls._parse_path(
                    parent.path if parent else '',
                    params
                )
                if params.get('value') is None:
                    params['value'] = 0
                newobj = cls.namedtuple(**params)
                result.append(newobj)
                result.extend(cls._build_tree(
                    child.get('_children', []), newobj, **global_params
                ))
        return result
