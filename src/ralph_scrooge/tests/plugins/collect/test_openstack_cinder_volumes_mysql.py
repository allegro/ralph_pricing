# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.plugins.collect.openstack_cinder_volumes_mysql import (
    CinderVolumesPlugin
)


class TestOpenStackCinderVolumesMysqlUsage(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.plugin = CinderVolumesPlugin()

    def _mock_sql_query(self, create_engine_mock, return_value):
        def execute_mock(sql):
            return return_value

        connection_mock = mock.MagicMock()
        connection_mock.execute.side_effect = execute_mock

        engine_mock = mock.MagicMock()
        engine_mock.connect.return_value = connection_mock

        create_engine_mock.return_value = engine_mock

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.create_engine')
    def test_get_usages_volume_type_present(self, create_engine_mock):
        self._mock_sql_query(
            create_engine_mock,
            [('111', '/vol/1', '321', 10, 10, '123@SSD-2', 'SSD-1')]
        )
        result = [x for x in self.plugin.get_usages(self.today, 'mysql')]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ('321', 10, 'SSD-1', '111: /vol/1'))

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.create_engine')
    def test_get_usages_volume_type_not_present(self, create_engine_mock):
        self._mock_sql_query(
            create_engine_mock,
            [('111', '/vol/1', '321', 10, 10, '123@SSD-2', None)]
        )
        result = [x for x in self.plugin.get_usages(self.today, 'mysql')]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ('321', 10, 'SSD-2', '111: /vol/1'))

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.create_engine')
    def test_get_usages_volume_type_and_host_null(self, create_engine_mock):
        self._mock_sql_query(
            create_engine_mock,
            [('111', '/vol/1', '321', 10, 10, None, None)]
        )
        result = [x for x in self.plugin.get_usages(self.today, 'mysql')]
        self.assertEqual(len(result), 0)

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.create_engine')
    @override_settings(OPENSTACK_CINDER_VOLUMES_DONT_CHARGE_FOR_SIZE=['SSD-1'])
    def test_get_usages_volume_type_dont_charge_for_size(
        self, create_engine_mock
    ):
        self._mock_sql_query(
            create_engine_mock,
            [('111', '/vol/1', '321', 240, 10, '123@SSD-2', 'SSD-1')]
        )
        result = [x for x in self.plugin.get_usages(self.today, 'mysql')]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ('321', 24, 'SSD-1', '111: /vol/1'))
