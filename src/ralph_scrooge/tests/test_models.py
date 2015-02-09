# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D


from ralph_scrooge import models
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.models import History, HistoricalHistory
from ralph_scrooge.tests.utils.factory import (
    DailyPricingObjectFactory,
    DynamicExtraCostFactory,
    ExtraCostFactory,
    ExtraCostTypeFactory,
    PricingObjectFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    SupportCostFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class TestHistory(ScroogeTestCase):
    def test_history_flow(self):
        current_now = datetime.datetime.now()
        obj = History(field1=11, field2='aa')
        obj.save()
        # check historical record
        self.assertEquals(obj.history.count(), 1)
        obj1 = obj.history.most_recent()
        self.assertEquals(obj1.field1, 11)
        self.assertEquals(obj1.field2, 'aa')

        history1 = obj.history.all()[:1].get()
        self.assertGreaterEqual(history1.active_from, current_now)
        self.assertEqual(history1.active_to, datetime.datetime.max)

        current_now = datetime.datetime.now()
        # change obj
        obj.field1 = 12
        obj.save()

        # check historical record
        self.assertEquals(obj.history.count(), 2)
        obj2 = obj.history.most_recent()
        self.assertEquals(obj2.field1, 12)
        self.assertEquals(obj2.field2, 'aa')

        history2, history1 = obj.history.all()[:2]
        self.assertEqual(history1.active_to, history2.active_from)
        self.assertEqual(history2.active_to, datetime.datetime.max)

    def test_history_without_changes(self):
        obj = History(field1=11, field2='aa')
        obj.save()

        # check historical record
        self.assertEquals(obj.history.count(), 1)
        obj.field1 = 11
        obj.save()

        self.assertEquals(obj.history.count(), 1)

    def test_history_delete(self):
        obj = History(field1=11, field2='aa')
        obj.save()
        obj_id = obj.pk
        # check historical record
        self.assertEquals(obj.history.count(), 1)

        obj.delete()

        self.assertEquals(HistoricalHistory.objects.count(), 1)
        history1 = HistoricalHistory.objects.all()[:1].get()
        self.assertEquals(history1.id, obj_id)
        self.assertLess(history1.active_to, datetime.datetime.now())


class TestModelDiff(ScroogeTestCase):
    def test_obj_diff(self):
        obj = History(field1=11, field2='b')
        obj.save()

        # changes "without changes"
        obj.field1 = 11
        self.assertFalse(obj.has_changed)

        # real changes
        obj.field2 = 'vvv'
        self.assertTrue(obj.has_changed)
        self.assertEquals(obj.diff, {'field2': ('b', 'vvv')})

    def test_obj2dict(self):
        obj = History(field1=11, field2='b')
        self.assertEquals(obj._dict, {'field1': 11, 'field2': 'b', 'id': None})


class TestPricingService(ScroogeTestCase):
    def _set_sample_usages(self):
        # 3 Pricing Services (1 tested and dependent from others)
        # usage types:
        self.ps1, self.ps2, self.ps3 = PricingServiceFactory.create_batch(3)
        se1 = ServiceEnvironmentFactory(service__pricing_service=self.ps1)
        se2 = ServiceEnvironmentFactory(service__pricing_service=self.ps1)

        ut1, ut2, ut3 = UsageTypeFactory.create_batch(3, usage_type='SU')

        models.ServiceUsageTypes(
            usage_type=ut1,
            pricing_service=self.ps2,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 30),
            percent=50,
        ).save()
        models.ServiceUsageTypes(
            usage_type=ut2,
            pricing_service=self.ps2,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 30),
            percent=50,
        ).save()
        models.ServiceUsageTypes(
            usage_type=ut3,
            pricing_service=self.ps3,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 30),
            percent=100,
        ).save()

        # sample usages
        models.DailyUsage(
            daily_pricing_object=DailyPricingObjectFactory(),
            type=ut1,
            date=datetime.date(2013, 10, 3),
            service_environment=se1,
            value=100,
        ).save()
        models.DailyUsage(
            daily_pricing_object=DailyPricingObjectFactory(),
            type=ut2,
            date=datetime.date(2013, 10, 20),
            service_environment=se1,
            value=100,
        ).save()
        models.DailyUsage(
            daily_pricing_object=DailyPricingObjectFactory(),
            type=ut1,
            date=datetime.date(2013, 10, 28),
            service_environment=se2,
            value=100,
            warehouse=WarehouseFactory(),
        ).save()
        models.DailyUsage(
            daily_pricing_object=DailyPricingObjectFactory(),
            type=ut3,
            date=datetime.date(2013, 10, 3),
            service_environment=se2,
            value=100,
        ).save()

    def test_get_dependent_services(self):
        self._set_sample_usages()
        result = self.ps1.get_dependent_services(
            date=datetime.date(2013, 10, 3),
        )
        self.assertEquals(set(result), set([self.ps2, self.ps3]))

    def test_get_dependent_services_subset(self):
        self._set_sample_usages()
        result = self.ps1.get_dependent_services(
            date=datetime.date(2013, 10, 28),
        )
        self.assertEquals(set(result), set([self.ps2]))

    def test_get_dependent_services_empty(self):
        self._set_sample_usages()
        result = self.ps1.get_dependent_services(
            date=datetime.date(2013, 11, 30)
        )
        self.assertEquals(set(result), set())


class TestDailyCost(ScroogeTestCase):
    def setUp(self):
        self.se1, self.se2 = ServiceEnvironmentFactory.create_batch(2)
        self.po1 = PricingObjectFactory(service_environment=self.se1)
        self.po2 = PricingObjectFactory(service_environment=self.se2)

        self.bu1 = ExtraCostTypeFactory()
        self.bu2 = UsageTypeFactory()
        self.bu3 = PricingServiceFactory()
        self.bu4 = PricingServiceFactory()

        self.wh1 = WarehouseFactory()
        self.wh2 = WarehouseFactory()

    def _sample_tree(self):
        return [
            {
                'service_environment': self.se1,
                'value': 10,
                'cost': D('100'),
                'type': self.bu1,
            },
            {
                'service_environment': self.se2,
                'value': 20,
                'cost': D('200'),
                'type': self.bu3,
                '_children': [
                    {
                        'service_environment': self.se2,
                        'value': 10,
                        'cost': D('100'),
                        'type': self.bu1,
                    },
                    {
                        'service_environment': self.se2,
                        'value': 10,
                        'cost': D('100'),
                        'type': self.bu4,
                        '_children': [
                            {
                                'service_environment': self.se2,
                                'value': 10,
                                'cost': D('100'),
                                'type': self.bu2,
                            }
                        ]
                    }
                ]
            }
        ]

    def _sample_global_params(self):
        return {
            'date': datetime.date(2014, 10, 11),
        }

    def _sample_tree_flat(self):
        tree = self._sample_tree()
        result = []

        def parse(l, depth, path):
            if '_children' in l:
                for ch in l.get('_children', []):
                    parse(ch, depth + 1, '/'.join((path, str(ch['type'].id))))
                del l['_children']
            l['depth'] = depth
            l['path'] = path
            l['type'] = l['type'].baseusage_ptr
            result.append(l)
        for ch in tree:
            parse(ch, 0, str(ch['type'].id))
        return result

    def test_build_tree(self):
        tree = self._sample_tree()
        global_params = self._sample_global_params()
        result = models.DailyCost.build_tree(tree, **global_params)
        self.assertEquals(len(result), 5)  # all nodes in sample tree
        self.assertEquals(models.DailyCost.objects.count(), 2)
        self.assertEquals(models.DailyCost.objects_tree.count(), 5)

        tree_flat = self._sample_tree_flat()

        def daily_cost2dict(d):
            result = {}
            for attr in [
                'service_environment', 'value', 'cost', 'type', 'path', 'depth'
            ]:
                result[attr] = getattr(d, attr, None)
            return result

        daily_costs_dicts = map(
            daily_cost2dict,
            models.DailyCost.objects_tree.all()
        )
        for t in tree_flat:
            self.assertIn(t, daily_costs_dicts)


class TestModelRepr(ScroogeTestCase):
    def test_extra_cost(self):
        extra_cost = ExtraCostFactory()
        result = unicode(extra_cost)
        self.assertEqual(result, '{} - {}'.format(
            extra_cost.service_environment,
            extra_cost.extra_cost_type
        ))

    def test_dynamic_extra_cost(self):
        dynamic_extra_cost = DynamicExtraCostFactory()
        result = unicode(dynamic_extra_cost)
        self.assertEqual(result, '{} ({}-{})'.format(
            dynamic_extra_cost.dynamic_extra_cost_type,
            dynamic_extra_cost.start,
            dynamic_extra_cost.end,
        ))

    def test_support(self):
        support_cost = SupportCostFactory()
        result = unicode(support_cost)
        self.assertEqual(result, '{} ({} - {})'.format(
            support_cost.pricing_object.name,
            support_cost.start,
            support_cost.end,
        ))
