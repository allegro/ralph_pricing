# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from ralph_scrooge import models
from ralph_scrooge.rest.allocationadmin import (
    NoDynamicExtraCostTypeError,
    NoExtraCostError,
    NoUsageTypeError,
    NoExtraCostTypeError,
    ServiceEnvironmentDoesNotExistError,
    TeamDoesNotExistError,
)
from ralph_scrooge.rest.common import get_dates
from ralph_scrooge.tests.utils import factory


class TestAllocationAdmin(TestCase):
    def setUp(self):
        User.objects.create_superuser('test', 'test@test.test', 'test')
        self.client = APIClient()
        self.client.login(username='test', password='test')

        self.date = datetime.date(year=2014, month=12, day=1)

    def test_get_allocation_admin_when_there_is_any_data(self):
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.maxDiff = None
        self.assertEquals(
            json.loads(response.content),
            {
                "baseusages": {
                    "name": "Base Usages",
                    "rows": [],
                    "template": "tabbaseusages.html",
                },
                'teamcosts': {
                    'name': 'Team Costs',
                    'rows': [],
                    'template': 'tabteamcosts.html',
                },
                'dynamicextracosts': {
                    'name': 'Dynamic Extra Costs',
                    'rows': [],
                    'template': 'tabdynamicextracosts.html',
                },
                'extracosts': {
                    'name': 'Extra Costs',
                    'rows': [{
                        'extra_cost_type': {
                            'id': 1,
                            'name': 'Other'
                        },
                        'extra_costs': [{}]
                    }, {
                        'extra_cost_type': {
                            'id': 2,
                            'name': 'Support'
                        },
                        'extra_costs': [{}]
                    }],
                    'template': 'tabextracostsadmin.html'
                },
            }
        )

    def test_get_base_usage_when_there_is_one_usage_type(self):
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['baseusages'],
            {
                "rows": [{
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'type': {
                        'id': usage_type.id,
                        'name': '{0}'.format(usage_type),
                    }
                }],
                "name": "Base Usages",
                "template": "tabbaseusages.html",
            }
        )

    def test_get_base_usage_when_there_is_one_usage_price(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
        )
        factory.UsagePriceFactory(
            type=usage_type,
            start=first_day,
            end=last_day,
            cost=cost,
            forecast_cost=forecast_cost
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['baseusages'],
            {
                "rows": [{
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                    'type': {
                        'id': usage_type.id,
                        'name': '{0}'.format(usage_type),
                    }
                }],
                "name": "Base Usages",
                "template": "tabbaseusages.html",
            }
        )

    def test_get_base_usage_when_there_is_one_usage_type_by_warehouse(self):
        warehouse = factory.WarehouseFactory(show_in_report=True)
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
            by_warehouse=True,
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['baseusages'],
            {
                "rows": [{
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'type': {
                        'id': usage_type.id,
                        'name': '{0}'.format(usage_type),
                    },
                    "warehouse": {
                        "id": warehouse.id,
                        "name": warehouse.name
                    }
                }],
                "name": "Base Usages",
                "template": "tabbaseusages.html",
            }
        )

    def test_get_base_usage_when_there_is_one_usage_price_by_warehouse(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        warehouse = factory.WarehouseFactory(show_in_report=True)
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
            by_warehouse=True,
        )
        factory.UsagePriceFactory(
            type=usage_type,
            start=first_day,
            end=last_day,
            cost=cost,
            forecast_cost=forecast_cost,
            warehouse=warehouse,
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['baseusages'],
            {
                "rows": [{
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                    'type': {
                        'id': usage_type.id,
                        'name': '{0}'.format(usage_type),
                    },
                    "warehouse": {
                        "id": warehouse.id,
                        "name": warehouse.name,
                    }
                }],
                "name": "Base Usages",
                "template": "tabbaseusages.html",
            }
        )

    def test_get_team_cost_when_there_is_one_team(self):
        team = factory.TeamFactory()
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['teamcosts'],
            {
                "rows": [{
                    'team': {
                        'id': team.id,
                        'name': team.name,
                    },
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'members': 0,
                }],
                "name": "Team Costs",
                "template": "tabteamcosts.html",
            }
        )

    def test_get_team_cost_when_there_is_one_team_cost(self):
        cost = 100.0
        forecast_cost = 200.0
        members = 4
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        team = factory.TeamFactory()
        factory.TeamCostFactory(
            team=team,
            start=first_day,
            end=last_day,
            cost=cost,
            forecast_cost=forecast_cost,
            members_count=members
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['teamcosts'],
            {
                "rows": [{
                    'team': {
                        'id': team.id,
                        'name': team.name,
                    },
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                    'members': members,
                }],
                "name": "Team Costs",
                "template": "tabteamcosts.html",
            }
        )

    def test_get_dynamic_extra_cost_when_there_is_one_type(self):
        dynamic_extra_cost_type = factory.DynamicExtraCostTypeFactory()
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['dynamicextracosts'],
            {
                "rows": [{
                    'dynamic_extra_cost_type': {
                        'id': dynamic_extra_cost_type.id,
                        'name': dynamic_extra_cost_type.name,
                    },
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                }],
                "name": "Dynamic Extra Costs",
                "template": "tabdynamicextracosts.html",
            }
        )

    def test_get_dynamic_extra_cost_when_there_is_one_type_and_cost(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        dynamic_extra_cost_type = factory.DynamicExtraCostTypeFactory()
        factory.DynamicExtraCostFactory(
            dynamic_extra_cost_type=dynamic_extra_cost_type,
            forecast_cost=forecast_cost,
            cost=cost,
            start=first_day,
            end=last_day,
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['dynamicextracosts'],
            {
                "rows": [{
                    'dynamic_extra_cost_type': {
                        'id': dynamic_extra_cost_type.id,
                        'name': dynamic_extra_cost_type.name,
                    },
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                }],
                "name": "Dynamic Extra Costs",
                "template": "tabdynamicextracosts.html",
            }
        )

    def test_get_extra_cost_when_there_is_one_additional_type(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['extracosts'],
            {
                'name': 'Extra Costs',
                'rows': [{
                    'extra_cost_type': {
                        'id': 1,
                        'name': 'Other'
                    },
                    'extra_costs': [{}]
                }, {
                    'extra_cost_type': {
                        'id': 2,
                        'name': 'Support'
                    },
                    'extra_costs': [{}]
                }, {
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{}]
                }],
                'template': 'tabextracostsadmin.html'
            }
        )

    def test_get_extra_cost_when_there_is_one_additional_type_and_cost(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()
        extra_cost = factory.ExtraCostFactory(
            extra_cost_type=extra_cost_type,
            start=first_day,
            end=last_day,
            cost=cost,
            forecast_cost=forecast_cost,
            service_environment=service_environment,
        )
        response = self.client.get(
            '/scrooge/rest/allocationadmin/{0}/{1}/'.format(
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['extracosts'],
            {
                'name': 'Extra Costs',
                'rows': [{
                    'extra_cost_type': {
                        'id': 1,
                        'name': 'Other'
                    },
                    'extra_costs': [{}]
                }, {
                    'extra_cost_type': {
                        'id': 2,
                        'name': 'Support'
                    },
                    'extra_costs': [{}]
                }, {
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'id': extra_cost.id,
                        'cost': extra_cost.cost,
                        'forecast_cost': extra_cost.forecast_cost,
                        'service': extra_cost.service_environment.service_id,
                        'env': extra_cost.service_environment.environment_id
                    }]
                }],
                'template': 'tabextracostsadmin.html'
            }
        )

    def test_save_base_usage_when_there_is_wrong_usage_type(self):
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
        )
        self.assertRaises(
            NoUsageTypeError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/baseusages/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'type': {
                        'id': 0,
                        'name': '{0}'.format(usage_type.name),
                    }
                }]
            },
            format='json'
        )

    def test_save_base_usage_when_there_is_no_by_warehouse(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
        )
        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/baseusages/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                    'type': {
                        'id': '{0}'.format(usage_type.id),
                        'name': '{0}'.format(usage_type.name),
                    }
                }]
            },
            format='json'
        )
        usage_price = models.UsagePrice.objects.all()[0]
        self.assertEquals(usage_price.cost, cost)
        self.assertEquals(usage_price.forecast_cost, forecast_cost)
        self.assertEquals(usage_price.start, first_day)
        self.assertEquals(usage_price.end, last_day)
        self.assertEquals(usage_price.type, usage_type)
        self.assertEquals(usage_price.warehouse, None)

    def test_save_base_usage_when_there_is_by_warehouse(self):
        warehouse = factory.WarehouseFactory()
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        usage_type = factory.UsageTypeFactory(
            is_manually_type=True,
            usage_type='BU',
        )
        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/baseusages/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'type': {
                        'id': '{0}'.format(usage_type.id),
                        'name': '{0}'.format(usage_type.name),
                    },
                    'warehouse': {
                        'id': warehouse.id,
                        'name': warehouse.name
                    }
                }]
            },
            format='json'
        )
        usage_price = models.UsagePrice.objects.all()[0]
        self.assertEquals(usage_price.start, first_day)
        self.assertEquals(usage_price.end, last_day)
        self.assertEquals(usage_price.type, usage_type)
        self.assertEquals(usage_price.warehouse, warehouse)

    def test_save_extra_cost_when_there_is_wrong_type(self):
        self.assertRaises(
            NoExtraCostTypeError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': 0,
                        'name': 'Other'
                    },
                    'extra_costs': [{}]
                }]
            },
            format='json'
        )

    def test_save_extra_cost_when_there_is_no_service(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )
        self.assertEquals(models.ExtraCost.objects.count(), 0)

    def test_save_extra_cost_when_there_is_bad_service(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'env': service_environment.environment_id,
                        'service': False
                    }]
                }]
            },
            format='json'
        )
        self.assertEquals(models.ExtraCost.objects.count(), 0)

    def test_save_extra_cost_when_there_is_no_env(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'service': service_environment.service_id,
                    }]
                }]
            },
            format='json'
        )
        self.assertEquals(models.ExtraCost.objects.count(), 0)

    def test_save_extra_cost_when_there_is_bad_env(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'service': service_environment.service_id,
                        'env': False,
                    }]
                }]
            },
            format='json'
        )
        self.assertEquals(models.ExtraCost.objects.count(), 0)

    def test_save_extra_cost_when_there_is_wrong_service(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.assertRaises(
            ServiceEnvironmentDoesNotExistError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'service': 111,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )

    def test_save_extra_cost_when_there_is_wrong_env(self):
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.assertRaises(
            ServiceEnvironmentDoesNotExistError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'service': service_environment.service_id,
                        'env': 111,
                    }]
                }]
            },
            format='json'
        )

    def test_save_extra_cost_when_everything_is_ok(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'cost': cost,
                        'forecast_cost': forecast_cost,
                        'service': service_environment.service_id,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )
        extra_cost = models.ExtraCost.objects.all()[0]
        self.assertEquals(extra_cost.cost, cost)
        self.assertEquals(extra_cost.forecast_cost, forecast_cost)
        self.assertEquals(extra_cost.service_environment, service_environment)
        self.assertEquals(extra_cost.extra_cost_type, extra_cost_type)

    def test_update_extra_cost_when_wrong_extra_cost(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()
        extra_cost = models.ExtraCost.objects.create(
            cost=50.0,
            forecast_cost=50.0,
            service_environment=service_environment,
            extra_cost_type=extra_cost_type,
            start=first_day,
            end=last_day,
        )
        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'id': extra_cost.id,
                        'cost': cost,
                        'forecast_cost': forecast_cost,
                        'service': service_environment.service_id,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )
        self.assertRaises(
            NoExtraCostError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'id': 0,
                        'cost': 0.0,
                        'forecast_cost': 0.0,
                        'service': service_environment.service_id,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )

    def test_update_extra_cost_when_everything_is_ok(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        extra_cost_type = factory.ExtraCostTypeFactory()
        service_environment = factory.ServiceEnvironmentFactory()
        extra_cost = models.ExtraCost.objects.create(
            cost=50.0,
            forecast_cost=50.0,
            service_environment=service_environment,
            extra_cost_type=extra_cost_type,
            start=first_day,
            end=last_day,
        )
        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/extracosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                'rows': [{
                    'extra_cost_type': {
                        'id': extra_cost_type.id,
                        'name': extra_cost_type.name
                    },
                    'extra_costs': [{
                        'id': extra_cost.id,
                        'cost': cost,
                        'forecast_cost': forecast_cost,
                        'service': service_environment.service_id,
                        'env': service_environment.environment_id,
                    }]
                }]
            },
            format='json'
        )
        extra_cost = models.ExtraCost.objects.all()[0]
        self.assertEquals(extra_cost.cost, cost)
        self.assertEquals(extra_cost.forecast_cost, forecast_cost)

    def test_save_dynamic_extra_cost_when_there_is_wrong_type(self):
        dynamic_extra_cost_type = factory.DynamicExtraCostTypeFactory()

        self.assertRaises(
            NoDynamicExtraCostTypeError,
            self.client.post,
            ('/scrooge/rest/allocationadmin/{0}/{1}/'
             'dynamicextracosts/save').format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'dynamic_extra_cost_type': {
                        'id': 0,
                        'name': dynamic_extra_cost_type.name,
                    },
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                }],
                "name": "Dynamic Extra Costs",
                "template": "tabdynamicextracosts.html",
            },
            format='json'
        )

    def test_save_dynamic_extra_cost(self):
        cost = 100.0
        forecast_cost = 200.0
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        dynamic_extra_cost_type = factory.DynamicExtraCostTypeFactory()

        self.client.post(
            ('/scrooge/rest/allocationadmin/{0}/{1}/'
             'dynamicextracosts/save').format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'dynamic_extra_cost_type': {
                        'id': dynamic_extra_cost_type.id,
                        'name': dynamic_extra_cost_type.name,
                    },
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                }],
                "name": "Dynamic Extra Costs",
                "template": "tabdynamicextracosts.html",
            },
            format='json'
        )

        dynamic_extra_cost = models.DynamicExtraCost.objects.all()[0]
        self.assertEquals(dynamic_extra_cost.cost, cost)
        self.assertEquals(dynamic_extra_cost.forecast_cost, forecast_cost)
        self.assertEquals(dynamic_extra_cost.start, first_day)
        self.assertEquals(dynamic_extra_cost.end, last_day)
        self.assertEquals(
            dynamic_extra_cost.dynamic_extra_cost_type,
            dynamic_extra_cost_type,
        )

    def test_save_team_costs_when_there_is_wrong_type(self):
        team = factory.TeamFactory()

        self.assertRaises(
            TeamDoesNotExistError,
            self.client.post,
            '/scrooge/rest/allocationadmin/{0}/{1}/teamcosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'team': {
                        'id': 0,
                        'name': team.name,
                    },
                    'cost': 0.0,
                    'forecast_cost': 0.0,
                    'members': 0,
                }],
            },
            format='json'
        )

    def test_save_team_costs(self):
        cost = 100.0
        forecast_cost = 200.0
        members = 4
        first_day, last_day, days_in_month = get_dates(
            self.date.year,
            self.date.month,
        )
        team = factory.TeamFactory()

        self.client.post(
            '/scrooge/rest/allocationadmin/{0}/{1}/teamcosts/save'.format(
                self.date.year,
                self.date.month,
            ),
            {
                "rows": [{
                    'team': {
                        'id': team.id,
                        'name': team.name,
                    },
                    'cost': cost,
                    'forecast_cost': forecast_cost,
                    'members': members,
                }],
            },
            format='json'
        )

        team_cost = models.TeamCost.objects.all()[0]
        self.assertEquals(team_cost.cost, cost)
        self.assertEquals(team_cost.forecast_cost, forecast_cost)
        self.assertEquals(team_cost.members_count, members)
        self.assertEquals(team_cost.start, first_day)
        self.assertEquals(team_cost.end, last_day)
        self.assertEquals(team_cost.team, team)
