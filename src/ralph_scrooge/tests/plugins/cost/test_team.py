# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
from datetime import date
from decimal import Decimal as D

from ralph_scrooge import models
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.plugins.cost.team import TeamPlugin
from ralph_scrooge.plugins.cost.base import NoPriceCostError
from ralph_scrooge.tests.utils.factory import (
    ServiceEnvironmentFactory,
    TeamCostFactory,
    TeamFactory,
)


class TestTeamPlugin(ScroogeTestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.date_out_of_range = date(2013, 11, 1)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        self.team_time = TeamFactory(billing_type=models.TeamBillingType.time)
        self.team_assets_cores = TeamFactory(
            billing_type=models.TeamBillingType.assets_cores,
        )
        self.team_assets = TeamFactory(
            billing_type=models.TeamBillingType.assets,
        )
        self.team_distribute = TeamFactory(
            billing_type=models.TeamBillingType.distribute,
        )
        self.team_average = TeamFactory(
            billing_type=models.TeamBillingType.average,
        )

        self.teams = models.Team.objects.all()

        # costs
        # team time
        team_time_cost = TeamCostFactory(
            cost=300,  # daily cost: 10
            forecast_cost=600,  # daily cost: 20
            start=self.start,
            end=self.end,
            team=self.team_time,
            members_count=10,
        )
        TeamCostFactory(
            cost=300,  # daily cost: 10
            forecast_cost=600,  # daily cost: 20
            start=self.start,
            end=self.end,
            team=self.team_assets_cores,
            members_count=20,
        )
        TeamCostFactory(
            cost=900,  # daily cost: 30
            forecast_cost=1800,  # daily cost: 60
            start=self.start,
            end=self.end,
            team=self.team_assets,
            members_count=20,
        )
        TeamCostFactory(
            cost=3000,  # daily cost: 100
            forecast_cost=1500,  # daily cost: 50
            start=self.start,
            end=self.end,
            team=self.team_distribute,
            members_count=10,
        )
        TeamCostFactory(
            cost=6000,  # daily cost: 200
            forecast_cost=3000,  # daily cost: 100
            start=self.start,
            end=self.end,
            team=self.team_average,
            members_count=10,
        )

        # service_environments
        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service_environments = models.ServiceEnvironment.objects.all()
        self.service_environments_subset = [
            self.service_environment1,
            self.service_environment2,
        ]

        # service_environments percentage (only for time team)
        percentage = [30, 40, 30]
        for service_environment, p in zip(
            self.service_environments,
            percentage
        ):
            tvp = models.TeamServiceEnvironmentPercent(
                team_cost=team_time_cost,
                service_environment=service_environment,
                percent=p,
            )
            tvp.save()

    # =========================================================================
    # TIME
    # =========================================================================
    def test_team_time_costs(self):
        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_time,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('3'),  # 30 % of daily cost 10
                    'type': self.team_time,
                    'percent': D('0.3'),  # divide by 30 days
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('4'),  # 40 % of daily cost 10
                    'type': self.team_time,
                    'percent': D('0.4'),
                }
            ]
        })

    def test_team_time_forecast_costs(self):
        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_time,
            forecast=True,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('6'),  # 30 % of daily cost 20
                    'type': self.team_time,
                    'percent': D('0.3'),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('8'),  # 40 % of daily cost 20
                    'type': self.team_time,
                    'percent': D('0.4'),
                }
            ]
        })

    def test_team_time_no_price_cost(self):
        with self.assertRaises(NoPriceCostError):
            TeamPlugin.costs(
                date=self.date_out_of_range,
                service_environments=self.service_environments_subset,
                team=self.team_time,
                forecast=False,
            )

    # =========================================================================
    # ASSETS & CORES COUNT
    # =========================================================================
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_assets_cores,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('3'),  # 200 / 500 * 5 + 20 / 100 * 5
                    'type': self.team_assets_cores,
                    'percent': D(3) / D(10),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('4'),  # 200 / 500 * 5 + 40 / 100 * 5
                    'type': self.team_assets_cores,
                    'percent': D(4) / D(10),
                }
            ]
        })

    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_forecast_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_assets_cores,
            forecast=True,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('6'),  # 200 / 500 * 10 + 20 / 100 * 10
                    'type': self.team_assets_cores,
                    'percent': D(6) / D(20),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('8'),  # 200 / 500 * 10 + 40 / 100 * 10
                    'type': self.team_assets_cores,
                    'percent': D(8) / D(20),
                }
            ]
        })

    def test_team_assets_cores_no_price_cost(self):
        with self.assertRaises(NoPriceCostError):
            TeamPlugin.costs(
                date=self.date_out_of_range,
                service_environments=self.service_environments_subset,
                team=self.team_assets_cores,
                forecast=False,
            )

    # =========================================================================
    # ASSETS COUNT
    # =========================================================================
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_costs(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 200,
        }
        total_assets_mock.return_value = 500

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_assets,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('12'),  # 200 / 500 * 30
                    'type': self.team_assets,
                    'percent': D(12) / D(30),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('12'),  # 100 / 500 * 30
                    'type': self.team_assets,
                    'percent': D(12) / D(30),
                }
            ]
        })

    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_forecast_costs(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 100,
            # self.service_environment3.id: 200,
        }
        total_assets_mock.return_value = 500

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_assets,
            forecast=True,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('24'),  # 200 / 500 * 60
                    'type': self.team_assets,
                    'percent': D(24) / D(60),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('12'),  # 100 / 500 * 60
                    'type': self.team_assets,
                    'percent': D(12) / D(60),
                }
            ]
        })

    def test_team_assets_no_price_cost(self):
        with self.assertRaises(NoPriceCostError):
            TeamPlugin.costs(
                date=self.date_out_of_range,
                service_environments=self.service_environments_subset,
                team=self.team_assets,
                forecast=False,
            )

    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_team_daily_cost')  # noqa
    def test_team_assets_cost_0(
        self,
        team_daily_cost_mock,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 0,
            self.service_environment2.id: 0,
        }
        total_assets_mock.return_value = 0
        team_daily_cost_mock.return_value = (0, 0, 0)
        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_assets,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('0'),
                    'type': self.team_assets,
                    'percent': D(0),
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('0'),
                    'type': self.team_assets,
                    'percent': D(0),
                }
            ]
        })

    # =========================================================================
    # DISTRIBUTION (BY MEMEBERS COUNT)
    # =========================================================================
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_distribute,
            forecast=False,
        )
        # daily cost: 100
        # members count: time - 10, assets&cores - 20, assets - 20
        # dependent teams daily costs:
        # time - 20 (10/50 * 100)
        # assets & cores - 40
        # assets - 40
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    # time: 30% * 20 = 6
                    # assets & cores: 200 / 500 * 20  + 20 / 100 * 20 = 12
                    # assets: 200 / 500 * 40 = 16
                    'cost': D('34'),
                    'type': self.team_distribute,
                    'percent': D(34) / 100,
                }
            ],
            self.service_environment2.id: [
                {
                    # time: 40% * 20 = 8
                    # assets & cores: 200 / 500 * 20  + 40 / 100 * 20 = 16
                    # assets: 200 / 500 * 40 = 16
                    'cost': D('40'),
                    'type': self.team_distribute,
                    'percent': D(40) / 100,
                }
            ]
        })

    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_forecast_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_distribute,
            forecast=True,
        )
        # daily cost: 50
        # members count: time - 10, assets&cores - 20, assets - 20
        # dependent teams daily costs:
        # time - 10 (10/50 * 50)
        # assets & cores - 20
        # assets - 20
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    # time: 30% * 10 = 3
                    # assets & cores: 200 / 500 * 10  + 20 / 100 * 10 = 6
                    # assets: 200 / 500 * 20 = 8
                    'cost': D('17'),
                    'type': self.team_distribute,
                    'percent': D(17) / 50,
                }
            ],
            self.service_environment2.id: [
                {
                    # time: 40% * 10 = 4
                    # assets & cores: 200 / 500 * 10  + 40 / 100 * 10 = 8
                    # assets: 200 / 500 * 20 = 8
                    'cost': D('20'),
                    'type': self.team_distribute,
                    'percent': D(20) / 50,
                }
            ]
        })

    def test_team_distribute_no_price_cost(self):
        with self.assertRaises(NoPriceCostError):
            TeamPlugin.costs(
                date=self.date_out_of_range,
                service_environments=self.service_environments_subset,
                team=self.team_distribute,
                forecast=False,
            )

    # =========================================================================
    # AVERAGE (FROM %)
    # =========================================================================
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_average_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_average,
            forecast=False,
        )
        # daily cost: 200
        # percentage:
        # time: se1 - 0.3, se2: 0.4
        # assets & cores: se1 - 0.3, se2 - 0.4
        # assets: se1 - 0.4, se2 - 0.4
        # distrubution: se1 - 0.34, se2 - 0.4
        # total: se1 - 1.34, se2 - 1.6
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('67'),  # 1.34 * 200 / 4 (total teams count)
                    'type': self.team_average,
                    'percent': D(67) / 200,
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('80'),  # 1.6 * 200 / 4
                    'type': self.team_average,
                    'percent': D(80) / 200,
                }
            ]
        })

    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.team.TeamPlugin._get_assets_count_by_service_environment')  # noqa
    def test_team_average_forecast_costs(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            # self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            # self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        costs = TeamPlugin.costs(
            date=self.today,
            service_environments=self.service_environments_subset,
            team=self.team_average,
            forecast=True,
        )
        # daily cost: 100
        # percentage:
        # time: se1 - 0.3, se2: 0.4
        # assets & cores: se1 - 0.3, se2 - 0.4
        # assets: se1 - 0.4, se2 - 0.4
        # distrubution: se1 - 0.34, se2 - 0.4
        # total: se1 - 1.34, se2 - 1.6
        self.assertEquals(costs, {
            self.service_environment1.id: [
                {
                    'cost': D('33.5'),  # 1.34 * 100 / 4 (total teams count)
                    'type': self.team_average,
                    'percent': D(33.5) / 100,
                }
            ],
            self.service_environment2.id: [
                {
                    'cost': D('40'),  # 1.6 * 100 / 4
                    'type': self.team_average,
                    'percent': D(40) / 100,
                }
            ]
        })

    def test_team_average_no_price_cost(self):
        with self.assertRaises(NoPriceCostError):
            TeamPlugin.costs(
                date=self.date_out_of_range,
                service_environments=self.service_environments_subset,
                team=self.team_average,
                forecast=False,
            )

    # TODO: test other methods
