# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
from collections import OrderedDict
from datetime import date
from decimal import Decimal as D, getcontext

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge import models
from ralph_scrooge.plugins.reports.team import Team
from ralph_scrooge.tests.utils.factory import (
    ServiceEnvironmentFactory,
    TeamCostFactory,
    TeamDaterangeFactory,
    TeamFactory,
)


class TestTeam(TestCase):
    def tearDown(self):
        # set up decimal divide_by to make comparisons easier
        decimal_context = getcontext()
        decimal_context.prec = self.__prev_decimal_prec

    def setUp(self):
        # set up decimal divide_by to make comparisons easier
        decimal_context = getcontext()
        self.__prev_decimal_prec = decimal_context.prec
        decimal_context.prec = 4

        self.plugin = Team

        # usage type
        # self.usage_type = models.UsageType(
        #     name='Teams',
        #     symbol='Teams',
        #     by_team=True,
        #     type='BU',
        # )
        # self.usage_type.save()

        # teams
        self.team_time = TeamFactory(show_percent_column=True)
        self.team_assets_cores = TeamFactory(
            billing_type=models.TeamBillingType.assets_cores,
        )
        self.team_assets = TeamFactory(
            billing_type=models.TeamBillingType.assets,
        )
        self.team_distribute = TeamFactory(
            billing_type=models.TeamBillingType.distribute,
        )
        self.teams = models.Team.objects.all()

        # dateranges
        self.daterange1 = TeamDaterangeFactory(
            team=self.team_time,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
        )
        self.daterange2 = TeamDaterangeFactory(
            team=self.team_time,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
        )

        # costs
        # team time
        TeamCostFactory(
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_time,
            members_count=10,
        )
        TeamCostFactory(
            cost=900,
            forecast_cost=450,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_time,
            members_count=20,
        )
        TeamCostFactory(
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 30),
            team=self.team_assets_cores,
            members_count=20,
        )
        TeamCostFactory(
            cost=800,
            forecast_cost=1600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
            team=self.team_assets,
            members_count=20,
        )
        TeamCostFactory(
            cost=100,
            forecast_cost=200,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
            team=self.team_assets,
            members_count=10,
        )
        TeamCostFactory(
            cost=3000,
            forecast_cost=1500,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_distribute,
            members_count=10,
        )
        TeamCostFactory(
            cost=6000,
            forecast_cost=3000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_distribute,
            members_count=10,
        )

        # service_environments
        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service_environments = models.ServiceEnvironment.objects.all()

        # service_environments percentage (only for time team)
        percentage = (
            (self.daterange1, [30, 30, 40]),
            (self.daterange2, [20, 50, 30]),
        )
        for team_daterange, percent in percentage:
            for service_environment, p in zip(
                self.service_environments,
                percent
            ):
                tvp = models.TeamServiceEnvironmentPercent(
                    team_daterange=team_daterange,
                    service_environment=service_environment,
                    percent=p,
                )
                tvp.save()

    def test_get_team_dateranges_percentage(self):
        result = self.plugin._get_team_dateranges_percentage(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_time,
        )
        self.assertEquals(result, {
            (date(2013, 10, 3), date(2013, 10, 10)): {
                self.service_environment1.id: 30,
                self.service_environment2.id: 30,
                self.service_environment3.id: 40,
            },
            (date(2013, 10, 11), date(2013, 10, 27)): {
                self.service_environment1.id: 20,
                self.service_environment2.id: 50,
                self.service_environment3.id: 30,
            },
        })

    def test_get_teams_dateranges_members_count(self):
        result = self.plugin._get_teams_dateranges_members_count(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            teams=self.teams,
        )
        self.assertEquals(result, {
            (date(2013, 10, 3), date(2013, 10, 10)): {
                self.team_time.id: 10,
                self.team_assets_cores.id: 20,
                self.team_assets.id: 20,
                self.team_distribute.id: 10,
            },
            (date(2013, 10, 11), date(2013, 10, 15)): {
                self.team_time.id: 10,
                self.team_assets_cores.id: 20,
                self.team_assets.id: 10,
                self.team_distribute.id: 10,
            },
            (date(2013, 10, 16), date(2013, 10, 27)): {
                self.team_time.id: 20,
                self.team_assets_cores.id: 20,
                self.team_assets.id: 10,
                self.team_distribute.id: 10,
            },
        })

    def test_team_time_cost(self):
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_time,
            service_environments=self.service_environments,
            forecast=False,
        )
        cost_key = 'team_{}_cost'.format(self.team_time.id)
        percent_key = 'team_{}_percent'.format(self.team_time.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('212'),
                percent_key: D('0.2163'),
            },
            self.service_environment2.id: {
                cost_key: D('458'),
                percent_key: D('0.4673'),
            },
            self.service_environment3.id: {
                cost_key: D('310'),
                percent_key: D('0.3163'),
            },
        })

    def test_team_time_cost_incomplete_price(self):
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_time,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(
            self.team_time.id)
        percent_key = 'team_{}_percent'.format(self.team_time.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    def test_team_time_cost_no_price(self):
        daterange = models.TeamDaterange(
            team=self.team_time,
            start=date(2013, 11, 1),
            end=date(2013, 11, 10),
        )
        daterange.save()
        for service_environment, percent in zip(
            self.service_environments,
            [30, 20, 50]
        ):
            tvp = models.TeamServiceEnvironmentPercent(
                team_daterange=daterange,
                service_environment=service_environment,
                percent=percent,
            )
            tvp.save()
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_time,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_time.id)
        percent_key = 'team_{}_percent'.format(self.team_time.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    def test_team_time_cost_forecast(self):
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_time,
            service_environments=self.service_environments,
            forecast=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_time.id)
        percent_key = 'team_{}_percent'.format(self.team_time.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('208'),
                percent_key: D('0.2364'),
            },
            self.service_environment2.id: {
                cost_key: D('376'),
                percent_key: D('0.4273'),
            },
            self.service_environment3.id: {
                cost_key: D('296'),
                percent_key: D('0.3364'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_cost(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_assets_cores,
            service_environments=self.service_environments,
            forecast=False,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets_cores.id)
        percent_key = 'team_{}_percent'.format(self.team_assets_cores.id)
        # cost (1-30): 300
        # cost (3-27): 250
        # daily cost: 250 / 25 = 10
        # assets cost in period: 10 * 25 / 2 = 125
        # cores cost in period: 10 * 25 / 2 = 125
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
                percent_key: D('0.3'),
            },
            self.service_environment2.id: {
                cost_key: D('100'),  # 0.4 * 125 + 0.4 * 125
                percent_key: D('0.4'),
            },
            self.service_environment3.id: {
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
                percent_key: D('0.3'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_cost_forecast(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_assets_cores,
            service_environments=self.service_environments,
            forecast=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets_cores.id)
        percent_key = 'team_{}_percent'.format(self.team_assets_cores.id)
        # forecast (1-30): 600
        # forecast (3-27): 500
        # daily cost: 500 / 25 = 20
        # assets cost in period: 20 * 25 / 2 = 250
        # cores cost in period: 20 * 25 / 2 = 250
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
                percent_key: D('0.3'),
            },
            self.service_environment2.id: {
                cost_key: D('200'),  # 0.4 * 250 + 0.4 * 250
                percent_key: D('0.4'),
            },
            self.service_environment3.id: {
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
                percent_key: D('0.3'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_cost_incomplete_price(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_assets_cores,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets_cores.id)
        percent_key = 'team_{}_percent'.format(self.team_assets_cores.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cores_cost_no_price(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 30,
            self.service_environment3.id: 60,
        }
        total_assets_mock.return_value = 120
        cores_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 60,
            self.service_environment3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_assets_cores,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets_cores.id)
        percent_key = 'team_{}_percent'.format(self.team_assets_cores.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cost(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_assets,
            service_environments=self.service_environments,
            forecast=False,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets.id)
        percent_key = 'team_{}_percent'.format(self.team_assets.id)
        # cost (1-10): 800
        # cost (11-30): 100
        # assets daily cost (1-10): 800 / 10 = 80
        # assets daily cost (11-30): 100 / 20 = 5
        # assets cost in period: (3-10): 8 / 10 * 800 = 640
        # assets cost in period: (11-27): 17 / 20 * 100 = 85
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('290'),  # 0.4 * 640 + 0.4 * 85
                percent_key: D('0.4'),
            },
            self.service_environment2.id: {
                cost_key: D('290'),  # 0.4 * 640 + 0.4 * 85
                percent_key: D('0.4'),
            },
            self.service_environment3.id: {
                cost_key: D('145'),  # 0.2 * 640 + 0.2 * 85
                percent_key: D('0.2'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cost_forecast(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 180,
            self.service_environment3.id: 90,
        }
        total_assets_mock.return_value = 300
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_assets,
            service_environments=self.service_environments,
            forecast=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets.id)
        percent_key = 'team_{}_percent'.format(self.team_assets.id)
        # cost (1-10): 1600
        # cost (11-30): 200
        # assets daily cost (1-10): 1600 / 10 = 160
        # assets daily cost (11-30): 200 / 20 = 10
        # assets cost in period: (3-10): 8 / 10 * 1600 = 1280
        # assets cost in period: (11-27): 17 / 20 * 200 = 170
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('145'),  # 0.1 * 1280 + 0.1 * 170
                percent_key: D('0.1'),
            },
            self.service_environment2.id: {
                cost_key: D('870'),  # 0.6 * 1280 + 0.6 * 170
                percent_key: D('0.6'),
            },
            self.service_environment3.id: {
                cost_key: D('435'),  # 0.3 * 1280 + 0.3 * 170
                percent_key: D('0.3'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cost_incomplete_price(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 20),
            end=date(2013, 11, 5),
            team=self.team_assets,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets.id)
        percent_key = 'team_{}_percent'.format(self.team_assets.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_assets_cost_no_price(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 30,
            self.service_environment3.id: 60,
        }
        total_assets_mock.return_value = 120

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_assets,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets.id)
        percent_key = 'team_{}_percent'.format(self.team_assets.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_cost(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,  # 25%
            self.service_environment2.id: 30,  # 25%
            self.service_environment3.id: 60,  # 50%
        }
        total_assets_mock.return_value = 120
        cores_count_mock.return_value = {
            self.service_environment1.id: 30,  # 20%
            self.service_environment2.id: 60,  # 40%
            self.service_environment3.id: 60,  # 40%
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_distribute,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_distribute.id)
        percent_key = 'team_{}_percent'.format(self.team_distribute.id)
        # description:
        # costs:
        #   1-15: cost = 3000
        #     members:                    Team1    Team2    Team3    Total
        #     3-10 (cost=8/15*3000=1600): 10(320)  20(640)  20(640)  50(1600)
        #     11-15 (cost=1000)           10(250)  20(500)  10(250)  40(1000)
        #   16-30: cost = 6000
        #     members:
        #     16-27 (cost=4/5*6000=4800)  20(1920)  20(1920)  10(960)  50(4800)

        # service_environment1 (30%, 20%):
        #   3-10:
        #       T1: 0.3 * 320 = 96
        #       T2: 0.25 * 320 + 0.2 * 320 = 144
        #       T3: 0.25 * 640 = 160
        #       Total: 400
        #   11-15:
        #       T1: 0.2 * 250 = 50
        #       T2: 0.25 * 250 + 0.2 * 250 = 112.5
        #       T3: 0.25 * 250 = 62.5
        #       Total: 225
        #   16-27:
        #       T1: 0.2 * 1920 = 384
        #       T2: 0.25 * 960 + 0.2 * 960 = 432
        #       T3: 0.25 * 960 = 240
        #       Total: 1056
        #   total: 1681

        # service_environment2 (30%, 50%):
        #   3-10:
        #       T1: 0.3 * 320 = 96
        #       T2: 0.25 * 320 + 0.4 * 320 = 208
        #       T3: 0.25 * 640 = 160
        #       Total: 464
        #   11-15:
        #       T1: 0.5 * 250 = 125
        #       T2: 0.25 * 250 + 0.4 * 250 = 162.5
        #       T3: 0.25 * 250 = 62.5
        #       Total: 350
        #   16-27:
        #       T1: 0.5 * 1920 = 960
        #       T2: 0.25 * 960 + 0.4 * 960 = 624
        #       T3: 0.25 * 960 = 240
        #       Total: 1824
        #   total: 2638

        # service_environment3 (40%, 30%):
        #   3-10:
        #       T1: 0.4 * 320 = 128
        #       T2: 0.5 * 320 + 0.4 * 320 = 288
        #       T3: 0.5 * 640 = 320
        #       Total: 736
        #   11-15:
        #       T1: 0.3 * 250 = 75
        #       T2: 0.5 * 250 + 0.4 * 250 = 225
        #       T3: 0.5 * 250 = 125
        #       Total: 425
        #   16-27:
        #       T1: 0.3 * 1920 = 576
        #       T2: 0.5 * 960 + 0.4 * 960 = 864
        #       T3: 0.5 * 960 = 480
        #       Total: 1920
        #   total: 3081

        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('1681'),
                percent_key: D('0.2272'),
            },
            self.service_environment2.id: {
                cost_key: D('2638'),
                percent_key: D('0.3565'),
            },
            self.service_environment3.id: {
                cost_key: D('3081'),
                percent_key: D('0.4164'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_cost_forecast(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 30,
            self.service_environment3.id: 60,
        }
        total_assets_mock.return_value = 120
        cores_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 60,
            self.service_environment3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_distribute,
            service_environments=self.service_environments,
            forecast=True,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_distribute.id)
        percent_key = 'team_{}_percent'.format(self.team_distribute.id)
        # forecast costs are half of costs
        # detailed calculations in `test_team_distribute_cost`
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('840.4'),
                percent_key: D('0.2271'),
            },
            self.service_environment2.id: {
                cost_key: D('1319'),
                percent_key: D('0.3565'),
            },
            self.service_environment3.id: {
                cost_key: D('1540'),
                percent_key: D('0.4162'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_cost_incomplete_price(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 30,
            self.service_environment3.id: 60,
        }
        total_assets_mock.return_value = 120
        cores_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 60,
            self.service_environment3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_distribute,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_distribute.id)
        percent_key = 'team_{}_percent'.format(self.team_distribute.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_team_distribute_cost_no_price(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 30,
            self.service_environment3.id: 60,
        }
        total_assets_mock.return_value = 120
        cores_count_mock.return_value = {
            self.service_environment1.id: 30,
            self.service_environment2.id: 60,
            self.service_environment3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_distribute,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_distribute.id)
        percent_key = 'team_{}_percent'.format(self.team_distribute.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_team_time_cost_per_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_team_assets_cores_cost_per_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_team_assets_cost_per_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_team_distributed_cost_per_service_environment')  # noqa
    def test_team_average_cost(
        self,
        distributed_mock,
        assets_mock,
        assets_cores_mock,
        time_team_mock,
    ):
        team_avg = TeamFactory(billing_type=models.TeamBillingType.average)
        team_avg.save()
        team_percent_key = lambda t: 'team_{}_percent'.format(t.id)

        time_percent_key = team_percent_key(self.team_time)
        time_team_mock.return_value = {
            self.service_environment1.id: {time_percent_key: D('0.3')},
            self.service_environment2.id: {time_percent_key: D('0.3')},
            self.service_environment3.id: {time_percent_key: D('0.4')},
        }

        assets_cores_percent_key = team_percent_key(self.team_assets_cores)
        assets_cores_mock.return_value = {
            self.service_environment1.id: {assets_cores_percent_key: D('1.0')},
            self.service_environment2.id: {assets_cores_percent_key: D('0')},
        }

        assets_percent_key = team_percent_key(self.team_assets)
        assets_mock.return_value = {
            self.service_environment1.id: {assets_percent_key: D('0.1')},
            self.service_environment2.id: {assets_percent_key: D('0.3')},
            self.service_environment3.id: {assets_percent_key: D('0.6')},
        }

        distribted_percent_key = team_percent_key(self.team_distribute)
        distributed_mock.return_value = {
            self.service_environment2.id: {distribted_percent_key: D('0.3')},
            self.service_environment3.id: {distribted_percent_key: D('0.7')},
        }

        # daily cost: 100
        TeamCostFactory(
            cost=1500,
            forecast_cost=2000,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=team_avg,
        )
        # daily cost: 200
        TeamCostFactory(
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 6),
            end=date(2013, 10, 25),
            team=team_avg,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(team_avg.id)
        percent_key = 'team_{}_percent'.format(team_avg.id)
        # service_environment1: 0.3 + 1.0 + 0.1 = 1.4
        # service_environment2: 0.3 + 0 + 0.3 + 0.3 = 0.9
        # service_environment3: 0.4 + 0.6 + 0.7 = 1.7
        # cost between 6 and 15: 100 * 10 = 1000
        # cost between 16 and 25: 200 * 10 = 2000
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('1050'),  # 1000 * 1.4 / 4 + 2000 * 1.4 / 4
                percent_key: D('0.35'),  # 1050 / 3000
            },
            self.service_environment2.id: {
                cost_key: D('675'),  # 1000 * 0.9 / 4 + 2000 * 0.9 / 4
                percent_key: D('0.225'),  # 675 / 3000
            },
            self.service_environment3.id: {
                cost_key: D('1275'),  # 1000 * 1.7 / 4 + 2000 * 1.7 / 4
                percent_key: D('0.425'),  # 1275 / 3000
            },
        })

    def test_team_average_cost_incomplete_price(self):
        team_avg = TeamFactory(billing_type=models.TeamBillingType.average)
        team_avg.save()
        # daily cost: 200
        TeamCostFactory(
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 10, 25),
            end=date(2013, 11, 5),
            team=team_avg,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(team_avg.id)
        percent_key = 'team_{}_percent'.format(team_avg.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    def test_team_average_cost_no_price(self):
        team_avg = TeamFactory(billing_type=models.TeamBillingType.average)
        team_avg.save()
        # daily cost: 200
        TeamCostFactory(
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        result = self.plugin._get_team_cost_per_service_environment(
            start=date(2013, 11, 2),
            end=date(2013, 11, 5),
            team=team_avg,
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(team_avg.id)
        percent_key = 'team_{}_percent'.format(team_avg.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.service_environment3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    def test_usages_by_time(self):
        result = self.plugin.costs(
            team=self.team_time,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_time.id)
        percent_key = 'team_{}_percent'.format(self.team_time.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('212'),
                percent_key: D('0.2163'),
            },
            self.service_environment2.id: {
                cost_key: D('458'),
                percent_key: D('0.4673'),
            },
            self.service_environment3.id: {
                cost_key: D('310'),
                percent_key: D('0.3163'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages_by_assets_cores(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.costs(
            team=self.team_assets_cores,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets_cores.id)
        percent_key = 'team_{}_percent'.format(self.team_assets_cores.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('75'),
                percent_key: D('0.3'),
            },
            self.service_environment2.id: {
                cost_key: D('100'),
                percent_key: D('0.4'),
            },
            self.service_environment3.id: {
                cost_key: D('75'),
                percent_key: D('0.3'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages_by_assets(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        result = self.plugin.costs(
            team=self.team_assets,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_assets.id)
        percent_key = 'team_{}_percent'.format(self.team_assets.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('290'),
                percent_key: D('0.4'),
            },
            self.service_environment2.id: {
                cost_key: D('290'),
                percent_key: D('0.4'),
            },
            self.service_environment3.id: {
                cost_key: D('145'),
                percent_key: D('0.2'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
            self.service_environment2.id: 200,
            self.service_environment3.id: 100,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
            self.service_environment2.id: 40,
            self.service_environment3.id: 40,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.costs(
            team=self.team_distribute,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=self.service_environments,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{}_cost'.format(self.team_distribute.id)
        percent_key = 'team_{}_percent'.format(self.team_distribute.id)
        self.assertEquals(result, {
            self.service_environment1.id: {
                cost_key: D('2188'),
                percent_key: D('0.2957'),
            },
            self.service_environment2.id: {
                cost_key: D('3145'),
                percent_key: D('0.425'),
            },
            self.service_environment3.id: {
                cost_key: D('2067'),
                percent_key: D('0.2793'),
            },
        })

    def test_usages_subservice_environments_by_time(self):
        result = self.plugin.costs(
            team=self.team_time,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=[self.service_environment1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'team_{}_cost'.format(self.team_time.id): D('212'),
                'team_{}_percent'.format(self.team_time.id): D('0.2163'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages_subservice_environments_by_assets_cores(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.costs(
            team=self.team_assets_cores,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=[self.service_environment1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'team_{}_percent'.format(self.team_assets_cores.id): D('0.3'),
                'team_{}_cost'.format(self.team_assets_cores.id): D('75'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages_subservice_environments_by_assets(
        self,
        assets_count_mock,
        total_assets_mock,
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
        }
        total_assets_mock.return_value = 500
        result = self.plugin.costs(
            team=self.team_assets,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=[self.service_environment1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'team_{}_percent'.format(self.team_assets.id): D('0.4'),
                'team_{}_cost'.format(self.team_assets.id): D('290'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_usages_subservice_environments_by_distribution(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.costs(
            team=self.team_distribute,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=[self.service_environment1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'team_{}_percent'.format(self.team_distribute.id): D('0.2957'),
                'team_{}_cost'.format(self.team_distribute.id): D('2188'),
            },
        })

    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_cores_count_by_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_total_assets_count')  # noqa
    @mock.patch('ralph_scrooge.plugins.reports.team.Team._get_assets_count_by_service_environment')  # noqa
    def test_total_cost(
        self,
        assets_count_mock,
        total_assets_mock,
        cores_count_mock,
        total_cores_mock
    ):
        assets_count_mock.return_value = {
            self.service_environment1.id: 200,
        }
        total_assets_mock.return_value = 500
        cores_count_mock.return_value = {
            self.service_environment1.id: 20,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.total_cost(
            team=self.team_time,
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            service_environments=[self.service_environment1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, D('212'))

    def test_exclude_service_environments(self):
        self.team_time.excluded_services.add(self.service_environment1.service)
        result = self.plugin._exclude_service_environments(
            self.team_time,
            self.service_environments
        )
        self.assertEquals(
            set(result),
            {self.service_environment2, self.service_environment3}
        )

    def test_exclude_service_environments_empty(self):
        result = self.plugin._exclude_service_environments(
            self.team_time,
            self.service_environments
        )
        self.assertEquals(result, self.service_environments)

    def test_schema_with_percent(self):
        result = self.plugin.schema(self.team_time)
        self.assertEquals(result, OrderedDict([
            ('team_{}_percent'.format(self.team_time.id), {
                'name': _("{} %".format(self.team_time.name)),
                'rounding': 4,
            }),
            ('team_{}_cost'.format(self.team_time.id), {
                'name': _("{} cost".format(self.team_time.name)),
                'currency': True,
                'total_cost': True,
            })
        ]))

    def test_schema_without_percent(self):
        result = self.plugin.schema(self.team_assets)
        self.assertEquals(result, OrderedDict([
            ('team_{}_cost'.format(self.team_assets.id), {
                'name': _("{} cost".format(self.team_assets.name)),
                'currency': True,
                'total_cost': True,
            }),
        ]))
