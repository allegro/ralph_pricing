# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from factory import (
    lazy_attribute,
    Sequence,
)
from factory.django import DjangoModelFactory

from ralph_scrooge import models


class ServiceFactory(DjangoModelFactory):
    FACTORY_FOR = models.Service

    name = Sequence(lambda n: 'Service #%s' % n)
    ci_uid = Sequence(lambda n: n)


class OwnerFactory(DjangoModelFactory):
    FACTORY_FOR = models.Owner

    first_name = "Scrooge"
    last_name = Sequence(lambda n: "McDuck {}".format(n))
    sAMAccountName = "qwerty"
    cmdb_id = Sequence(lambda n: n)

    @lazy_attribute
    def email(self):
        return '{}.{}@example.com'.format(self.first_name, self.last_name)


class BusinessLineFactory(DjangoModelFactory):
    FACTORY_FOR = models.BusinessLine

    name = Sequence(lambda n: 'Business Line #%s' % n)
    ci_uid = Sequence(lambda n: n)
