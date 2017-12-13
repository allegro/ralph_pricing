# -*- coding: utf-8 -*-

from ralph_scrooge.plugins.subscribers.service_environment import (
    service_environment,
    validate_service_data
)
from ralph_scrooge.tests import ScroogeTestCase


CREATE_EVENT_DATA = {
    u'status': u'non_production',
    u'name': u'test-scrooge-4',
    u'tags': [],
    u'requires': [],
    u'technicalOwners': [
        {
            u'username': u'root',
            u'firstName': u'',
            u'area': None,
            u'lastName': u'',
            u'email': u'sc-noreply@allegrogroup.com',
            u'id': 1,
            u'areas': []
        }
    ],
    u'environments': [u'dev'],
    u'requiredBy': [],
    u'serviceId': None,
    u'incidentQueue': u'',
    u'branch': {
        u'name': u'replica-1',
        u'parent': 1,
        u'profitCenter': u'',
        u'slugPath': u'test.replica',
        u'id': 7,
        u'path': u'test > replica-1',
        u'slug': u'replica'
    },
    u'changedFields': [],
    u'businessOwners': [
        {
            u'username': u'root',
            u'firstName': u'',
            u'area': None,
            u'lastName': u'',
            u'email': u'sc-noreply@allegrogroup.com',
            u'id': 1,
            u'areas': []
        }
    ],
    u'groups': [],
    u'technicalBreakPolicy': u'',
    u'id': 9,
    u'isActive': True,
    u'uid': u'sc-9'
}


class TestServiceEnvironment(ScroogeTestCase):
    def test_service_environment(self):
        service_environment(CREATE_EVENT_DATA)

    def test_validate_service_data_checks_uid(self):
        errors = validate_service_data({'name': 'sc'})
        self.assertEqual(len(errors), 1)
        self.assertIn('uid', errors[0])

    def test_validate_service_data_checks_name(self):
        errors = validate_service_data({'uid': 'sc-1'})
        self.assertEqual(len(errors), 1)
        self.assertIn('name', errors[0])

    def test_validate_service_data_returns_no_errors(self):
        errors = validate_service_data({'uid': 'sc-1', 'name': 'sc'})
        self.assertEqual(len(errors), 0)
