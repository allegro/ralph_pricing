# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.plugins.collect.database import (
    get_database_model,
    get_unknown_service_environment,
    save_database_info,
    save_daily_database_info,
    database as database_plugin,
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DatabaseInfoFactory,
    PricingObjectModelFactory,
    ServiceEnvironmentFactory,
)

DATABASE_TYPES = ['MySQL']
UNKNOWN_SERVICE_ENVIRONMENT = ('db-1', 'env1')
TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'database': {
            DATABASE_TYPES[0]: UNKNOWN_SERVICE_ENVIRONMENT,
        }
    },
    DATABASE_TYPES=DATABASE_TYPES,
)


class TestDatabaseCollectPlugin(TestCase):
    def setUp(self):
        self.service_environment = ServiceEnvironmentFactory()
        self.unknown_service_environment = ServiceEnvironmentFactory(
            service__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
        )
        self.asset_info = AssetInfoFactory()
        self.today = datetime.date(2014, 7, 1)
        self.model = PricingObjectModelFactory(
            type_id=PRICING_OBJECT_TYPES.DATABASE,
            name=DATABASE_TYPES[0],
        )

    def _get_sample_database(self):
        return {
            'database_id': 1,
            'service_id': self.service_environment.service.id,
            'environment_id': self.service_environment.environment.id,
            'name': 'DB1',
            'parent_device_id': self.asset_info.device_id,
            'type': DATABASE_TYPES[0],
            'type_id': self.model.model_id,
        }

    def _compare_databases(self, sample_database, database_info):
        self.assertEquals(
            database_info.database_id,
            sample_database['database_id']
        )
        self.assertEquals(database_info.name, sample_database['name'])
        self.assertEquals(
            database_info.parent_device.device_id,
            sample_database['parent_device_id']
        )
        self.assertEquals(
            database_info.model.model_id,
            sample_database['type_id']
        )
        self.assertEquals(database_info.model.name, sample_database['type'])
        self.assertEquals(database_info.type_id, PRICING_OBJECT_TYPES.DATABASE)

    def test_get_database_model(self):
        sample_database = self._get_sample_database()
        model = get_database_model(sample_database)
        self.assertEquals(model, self.model)

    def test_save_database_info(self):
        sample_database = self._get_sample_database()
        sample_database['service_id'] = self.service_environment.service.ci_id
        sample_database['environment_id'] = (
            self.service_environment.environment.ci_id
        )
        created, database_info = save_database_info(
            sample_database,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_databases(sample_database, database_info)
        self.assertEquals(
            database_info.service_environment,
            self.service_environment
        )

    def test_save_database_info_invalid_service_environment(self):
        service_environment = ServiceEnvironmentFactory.build()
        sample_db = self._get_sample_database()
        sample_db['service_id'] = service_environment.service.ci_id
        sample_db['environment_id'] = service_environment.environment.ci_id
        created, database_info = save_database_info(
            sample_db,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_databases(sample_db, database_info)
        self.assertEquals(
            database_info.service_environment,
            self.unknown_service_environment
        )

    def test_save_daily_database_info(self):
        database_info = DatabaseInfoFactory()
        sample_database = self._get_sample_database()
        result = save_daily_database_info(
            sample_database,
            database_info,
            self.today
        )
        self.assertEquals(result.database_info, database_info)
        self.assertEquals(result.pricing_object, database_info)
        self.assertEquals(result.date, self.today)
        self.assertEquals(
            result.service_environment,
            database_info.service_environment
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_database_unknown_service_environment(self):
        service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.assertEquals(
            service_environment,
            get_unknown_service_environment(DATABASE_TYPES[0])
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_database_unknown_service_invalid_config(self):
        ServiceEnvironmentFactory()
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('DB2')

    def test_get_database_unknown_service_not_configured(self):
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('DB2')

    @mock.patch('ralph_scrooge.plugins.collect.database.api_scrooge.get_databases')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.database.update_database')
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_database_plugin(
        self,
        update_database_mock,
        get_databases_mock
    ):
        unknown_service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        update_database_mock.return_value = True
        databases_list = [self._get_sample_database()] * 5
        get_databases_mock.return_value = databases_list
        result = database_plugin(self.today)
        self.assertEquals(
            result,
            (True, 'Databases: 5 new, 0 updated, 5 total')
        )
        self.assertEquals(update_database_mock.call_count, 5)
        update_database_mock.assert_any_call(
            databases_list[0],
            self.today,
            unknown_service_environment,
        )

    @mock.patch('ralph_scrooge.plugins.collect.database.get_unknown_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.database.logger')
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_database_plugin_unknown_service_not_configured(
        self,
        logger_mock,
        get_unknown_service_environment_mock
    ):
        get_unknown_service_environment_mock.side_effect = (
            UnknownServiceEnvironmentNotConfiguredError()
        )
        result = database_plugin(self.today)
        self.assertTrue(logger_mock.error.called)
        self.assertEquals(
            result,
            (True, 'Databases: 0 new, 0 updated, 0 total')
        )
