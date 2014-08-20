# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db


class PathFieldNotConfiguredError(Exception):
    pass


class MultiPathNode(db.Model):
    _path_link = '/'
    _path_field = None

    path = db.CharField(max_length=255, db_index=True)
    depth = db.PositiveIntegerField(default=0)
    parent = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(MultiPathNode, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self._path_field:
            raise PathFieldNotConfiguredError()
        if self.parent is not None:
            self.path = self._create_path(self.parent.path)
            self.depth = self.parent.depth + 1
        else:
            self.path = self._create_path('')
        return super(MultiPathNode, self).save(*args, **kwargs)

    def _create_path(self, parent_path):
        """
        Returns path as join of parent path with value of current object path
        field value.
        """
        path_field_value = getattr(self, self._path_field)
        l = []
        if parent_path:
            l.append(parent_path)
        l.append(path_field_value)
        return self._path_link.join(map(str, l))

    def add_child(self, **kwargs):
        """
        Adds single child to object (link self as parent).
        """
        newobj = self.__class__(**kwargs)
        newobj.parent = self
        newobj.save()
        return newobj

    @classmethod
    def build_tree(cls, tree, parent=None, **global_params):
        """
        Build MultiPath tree Nodes according to tree list

        :param list tree: list of dicts. dict values will be passed as kwargs
            to new objects. Dict '_children' list value will be used to create
            node children.
        """
        assert isinstance(tree, (list, tuple))
        for child in tree:
            assert isinstance(child, dict)
            params = dict([(k, v) for k, v in child.items() if not k.startswith('_')])
            params.update(global_params)
            if parent is None:
                newobj = cls(**params)
                newobj.save()
            else:
                parent.add_child(**params)
            cls.build_tree(child.get('_children', []), newobj)
