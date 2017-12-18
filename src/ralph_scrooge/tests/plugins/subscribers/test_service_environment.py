# -*- coding: utf-8 -*-
from ralph_scrooge.models import Environment, OwnershipType, Service
from ralph_scrooge.plugins.subscribers.service_environment import (
    service_environment,
    _validate_service_data,
    _add_new_environments,
    _update_service,
    _update_owners,
    _update_environments)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import ServiceFactory, UserFactory


CREATE_EVENT_DATA = {
    u'name': u'test-scrooge-ąść',
    u'technicalOwners': [
        {
            u'username': u'tech',
            u'firstName': u'',
            u'area': None,
            u'lastName': u'',
            u'email': u'test@example.com',
            u'id': 1,
            u'areas': []
        }
    ],
    u'environments': [u'dev'],
    u'businessOwners': [
        {
            u'username': u'business',
            u'firstName': u'',
            u'area': None,
            u'lastName': u'',
            u'email': u'test@example.com',
            u'id': 1,
            u'areas': []
        }
    ],
    u'uid': u'sc-9'
}


class TestServiceEnvironment(ScroogeTestCase):
    def test_service_environment_adds_new_service(self):
        service_environment(CREATE_EVENT_DATA)
        service = Service.objects.filter(ci_uid=CREATE_EVENT_DATA['uid'])

        self.assertEqual(service.count(), 1)

    def test_validate_service_data_checks_uid(self):
        errors = _validate_service_data({'name': 'sc'})
        self.assertEqual(len(errors), 1)
        self.assertIn('uid', errors[0])

    def test_validate_service_data_checks_name(self):
        errors = _validate_service_data({'uid': 'sc-1'})
        self.assertEqual(len(errors), 1)
        self.assertIn('name', errors[0])

    def test_validate_service_data_returns_no_errors(self):
        errors = _validate_service_data({'uid': 'sc-1', 'name': 'sc'})
        self.assertEqual(len(errors), 0)

    def test__add_new_environments(self):
        envs = ['test_env_1', 'test_env_2']

        _add_new_environments(envs)

        envs_obj = Environment.objects.filter(name__in=envs)
        self.assertEqual(len(envs_obj), len(envs))

    def test__update_environments_add_new(self):
        service = ServiceFactory()
        envs = ['test_env_1', 'test_env_2']
        envs_obj = _add_new_environments(envs)

        _update_environments(service, envs_obj)

        self.assertEqual(service.environments.count(), 2)

    def test__update_environments_remove_environment(self):
        service = ServiceFactory()
        envs = ['test_env_1', 'test_env_2']
        envs_obj = _add_new_environments(envs)

        _update_environments(service, envs_obj)
        _update_environments(service, [envs_obj[0]])

        self.assertEqual(service.environments.count(), 1)

    def test__update_service(self):
        _update_service(CREATE_EVENT_DATA)

        self.assertEqual(
            Service.objects.filter(ci_uid='sc-9').count(), 1
        )

    def test__update_owners_add_owners(self):
        service = ServiceFactory()
        user_technical = UserFactory(username='tech')
        user_business = UserFactory(username='business')

        _update_owners(service, CREATE_EVENT_DATA)
        owner_technical = service.serviceownership_set.filter(
            owner_id=user_technical.id
        )
        owner_business = service.serviceownership_set.filter(
            owner_id=user_business.id
        )

        self.assertEqual(owner_technical.count(), 1)
        self.assertEqual(owner_business.count(), 1)
        self.assertEqual(owner_technical.first().type, OwnershipType.technical)
        self.assertEqual(owner_business.first().type, OwnershipType.business)

    def test__update_owners_remove_owners(self):
        service = ServiceFactory()
        user_technical = UserFactory(username='tech')
        user_business = UserFactory(username='business')
        data = CREATE_EVENT_DATA.copy()

        _update_owners(service, data)
        del data['technicalOwners']
        del data['businessOwners']
        _update_owners(service, data)
        owner_technical = service.serviceownership_set.filter(
            owner_id=user_technical.id
        )
        owner_business = service.serviceownership_set.filter(
            owner_id=user_business.id
        )

        self.assertEqual(owner_technical.count(), 0)
        self.assertEqual(owner_business.count(), 0)
