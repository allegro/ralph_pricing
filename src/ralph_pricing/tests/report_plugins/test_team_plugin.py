# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
from datetime import date
from decimal import Decimal as D

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_pricing import models
from ralph_pricing.plugins.reports.team import Team


class TestTeamPlugin(TestCase):
    def setUp(self):
        self.plugin = Team

        # usage type
        self.usage_type = models.UsageType(
            name='Teams',
            symbol='Teams',
            by_team=True,
            type='BU',
        )
        self.usage_type.save()

        # teams
        self.team_time = models.Team(
            name='T1',
            billing_type='TIME',
        )
        self.team_time.save()
        self.team_devices_cores = models.Team(
            name='T2',
            billing_type='DEVICES_CORES',
        )
        self.team_devices_cores.save()
        self.team_devices = models.Team(
            name='T3',
            billing_type='DEVICES',
        )
        self.team_devices.save()
        self.team_distribute = models.Team(
            name='T4',
            billing_type='DISTRIBUTE',
        )
        self.team_distribute.save()
        self.teams = models.Team.objects.all()

        # members count
        mc = models.TeamMembersCount(
            team=self.team_time,
            start=date(2013, 10, 1),
            end=date(2013, 10, 30),
            members_count=10,
        )
        mc.save()

        mc = models.TeamMembersCount(
            team=self.team_devices_cores,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
            members_count=10,
        )
        mc.save()
        mc = models.TeamMembersCount(
            team=self.team_devices_cores,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
            members_count=20,
        )
        mc.save()

        mc = models.TeamMembersCount(
            team=self.team_devices,
            start=date(2013, 10, 1),
            end=date(2013, 10, 20),
            members_count=20,
        )
        mc.save()
        mc = models.TeamMembersCount(
            team=self.team_devices,
            start=date(2013, 10, 21),
            end=date(2013, 10, 30),
            members_count=10,
        )
        mc.save()

        # costs
        # team time
        up = models.UsagePrice(
            type=self.usage_type,
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_time,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=900,
            forecast_cost=450,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_time,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 30),
            team=self.team_devices_cores,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=800,
            forecast_cost=1600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
            team=self.team_devices,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=100,
            forecast_cost=200,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
            team=self.team_devices,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=3000,
            forecast_cost=1500,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_distribute,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=6000,
            forecast_cost=3000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_distribute,
        )
        up.save()

        # ventures
        self.venture1 = models.Venture(name='V1', venture_id=1, is_active=True)
        self.venture1.save()
        self.venture2 = models.Venture(name='V2', venture_id=2, is_active=True)
        self.venture2.save()
        self.venture3 = models.Venture(name='V3', venture_id=3, is_active=True)
        self.venture3.save()
        self.ventures = models.Venture.objects.all()

        # ventures percentage (only for time team)
        percentage = (
            (date(2013, 10, 1), date(2013, 10, 10), [30, 30, 40]),
            (date(2013, 10, 11), date(2013, 10, 30), [20, 50, 30]),
        )
        for start, end, percent in percentage:
            for venture, p in zip(self.ventures, percent):
                tvp = models.TeamVenturePercent(
                    team=self.team_time,
                    venture=venture,
                    start=start,
                    end=end,
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
                self.venture1.id: 30,
                self.venture2.id: 30,
                self.venture3.id: 40,
            },
            (date(2013, 10, 11), date(2013, 10, 27)): {
                self.venture1.id: 20,
                self.venture2.id: 50,
                self.venture3.id: 30,
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
                self.team_devices_cores.id: 10,
                self.team_devices.id: 20,
            },
            (date(2013, 10, 11), date(2013, 10, 20)): {
                self.team_time.id: 10,
                self.team_devices_cores.id: 20,
                self.team_devices.id: 20,
            },
            (date(2013, 10, 21), date(2013, 10, 27)): {
                self.team_time.id: 10,
                self.team_devices_cores.id: 20,
                self.team_devices.id: 10,
            },
        })

    def test_team_time_cost(self):
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_time,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
        )
        percent_key = 'team_{0}_percent'.format(self.team_time.id)
        cost_key = 'team_{0}_cost'.format(self.team_time.id)
        self.assertEquals(result, {
            self.venture1.id: {
                percent_key: 23.2,
                cost_key: D('212'),
            },
            self.venture2.id: {
                percent_key: 43.6,
                cost_key: D('458'),
            },
            self.venture3.id: {
                percent_key: 33.2,
                cost_key: D('310'),
            },
        })

    def test_team_time_cost_incomplete_price(self):
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_time,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        percent_key = 'team_{0}_percent'.format(self.team_time.id)
        cost_key = 'team_{0}_cost'.format(self.team_time.id)
        self.assertEquals(result, {
            self.venture1.id: {
                percent_key: 18.82,
                cost_key: _('Incomplete price'),
            },
            self.venture2.id: {
                percent_key: 36.47,
                cost_key: _('Incomplete price'),
            },
            self.venture3.id: {
                percent_key: 27.06,
                cost_key: _('Incomplete price'),
            },
        })

    def test_team_time_cost_no_price(self):
        for venture, percent in zip(self.ventures, [30, 20, 50]):
            tvp = models.TeamVenturePercent(
                team=self.team_time,
                venture=venture,
                start=date(2013, 11, 1),
                end=date(2013, 11, 10),
                percent=percent,
            )
            tvp.save()
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_time,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        percent_key = 'team_{0}_percent'.format(self.team_time.id)
        cost_key = 'team_{0}_cost'.format(self.team_time.id)
        self.assertEquals(result, {
            self.venture1.id: {
                percent_key: 30,
                cost_key: _('No price'),
            },
            self.venture2.id: {
                percent_key: 20,
                cost_key: _('No price'),
            },
            self.venture3.id: {
                percent_key: 50,
                cost_key: _('No price'),
            },
        })

    def test_team_time_cost_forecast(self):
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_time,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=True,
        )
        percent_key = 'team_{0}_percent'.format(self.team_time.id)
        cost_key = 'team_{0}_cost'.format(self.team_time.id)
        self.assertEquals(result, {
            self.venture1.id: {
                percent_key: 23.2,
                cost_key: D('208'),
            },
            self.venture2.id: {
                percent_key: 43.6,
                cost_key: D('376'),
            },
            self.venture3.id: {
                percent_key: 33.2,
                cost_key: D('296'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cores_cost(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
            self.venture2.id: 200,
            self.venture3.id: 100,
        }
        total_devices_mock.return_value = 500
        cores_count_mock.return_value = {
            self.venture1.id: 20,
            self.venture2.id: 40,
            self.venture3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_devices_cores,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices_cores.id)
        cores_key = 'team_{0}_cores'.format(self.team_devices_cores.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices_cores.id)
        # cost (1-30): 300
        # cost (3-27): 250
        # daily cost: 250 / 25 = 10
        # devices cost in period: 10 * 25 / 2 = 125
        # cores cost in period: 10 * 25 / 2 = 125
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 8,
                cores_key: 0.8,
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
            },
            self.venture2.id: {
                devices_key: 8,
                cores_key: 1.6,
                cost_key: D('100'),  # 0.4 * 125 + 0.4 * 125
            },
            self.venture3.id: {
                devices_key: 4,
                cores_key: 1.6,
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cores_cost_forecast(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
            self.venture2.id: 200,
            self.venture3.id: 100,
        }
        total_devices_mock.return_value = 500
        cores_count_mock.return_value = {
            self.venture1.id: 20,
            self.venture2.id: 40,
            self.venture3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_devices_cores,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices_cores.id)
        cores_key = 'team_{0}_cores'.format(self.team_devices_cores.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices_cores.id)
        # forecast (1-30): 600
        # forecast (3-27): 500
        # daily cost: 500 / 25 = 20
        # devices cost in period: 20 * 25 / 2 = 250
        # cores cost in period: 20 * 25 / 2 = 250
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 8,
                cores_key: 0.8,
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
            },
            self.venture2.id: {
                devices_key: 8,
                cores_key: 1.6,
                cost_key: D('200'),  # 0.4 * 250 + 0.4 * 250
            },
            self.venture3.id: {
                devices_key: 4,
                cores_key: 1.6,
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cores_cost_incomplete_price(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
            self.venture2.id: 200,
            self.venture3.id: 100,
        }
        total_devices_mock.return_value = 500
        cores_count_mock.return_value = {
            self.venture1.id: 20,
            self.venture2.id: 40,
            self.venture3.id: 40,
        }
        total_cores_mock.return_value = 100

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_devices_cores,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices_cores.id)
        cores_key = 'team_{0}_cores'.format(self.team_devices_cores.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices_cores.id)
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 5.88,
                cores_key: 0.59,
                cost_key: _('Incomplete price'),
            },
            self.venture2.id: {
                devices_key: 5.88,
                cores_key: 1.18,
                cost_key: _('Incomplete price'),
            },
            self.venture3.id: {
                devices_key: 2.94,
                cores_key: 1.18,
                cost_key: _('Incomplete price'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cores_cost_no_price(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 60,
            self.venture3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_devices_cores,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices_cores.id)
        cores_key = 'team_{0}_cores'.format(self.team_devices_cores.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices_cores.id)
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 10,
                cores_key: 10,
                cost_key: _('No price'),
            },
            self.venture2.id: {
                devices_key: 10,
                cores_key: 20,
                cost_key: _('No price'),
            },
            self.venture3.id: {
                devices_key: 20,
                cores_key: 20,
                cost_key: _('No price'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cost(
        self,
        devices_count_mock,
        total_devices_mock,
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 180,
            self.venture3.id: 90,
        }
        total_devices_mock.return_value = 300
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_devices,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices.id)
        # cost (1-10): 800
        # cost (11-30): 100
        # devices daily cost (1-10): 800 / 10 = 80
        # devices daily cost (11-30): 100 / 20 = 5
        # devices cost in period: (3-10): 8 / 10 * 800 = 640
        # devices cost in period: (11-27): 17 / 20 * 100 = 85
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 2.4,  # (30 + 30) / 25
                cost_key: D('72.5'),  # 0.1 * 640 + 0.1 * 85
            },
            self.venture2.id: {
                devices_key: 14.4,  # (180 + 180) / 25
                cost_key: D('435'),  # 0.6 * 640 + 0.6 * 85
            },
            self.venture3.id: {
                devices_key: 7.2,  # (90 + 90) / 25
                cost_key: D('217.5'),  # 0.3 * 640 + 0.3 * 85
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cost_forecast(
        self,
        devices_count_mock,
        total_devices_mock,
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 180,
            self.venture3.id: 90,
        }
        total_devices_mock.return_value = 300
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_devices,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices.id)
        # cost (1-10): 1600
        # cost (11-30): 200
        # devices daily cost (1-10): 1600 / 10 = 160
        # devices daily cost (11-30): 200 / 20 = 10
        # devices cost in period: (3-10): 8 / 10 * 1600 = 1280
        # devices cost in period: (11-27): 17 / 20 * 200 = 170
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 2.4,  # (30 + 30) / 25
                cost_key: D('145'),  # 0.1 * 1280 + 0.1 * 170
            },
            self.venture2.id: {
                devices_key: 14.4,  # (180 + 180) / 25
                cost_key: D('870'),  # 0.6 * 1280 + 0.6 * 170
            },
            self.venture3.id: {
                devices_key: 7.2,  # (90 + 90) / 25
                cost_key: D('435'),  # 0.3 * 1280 + 0.3 * 170
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cost_incomplete_price(
        self,
        devices_count_mock,
        total_devices_mock,
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
            self.venture2.id: 200,
            self.venture3.id: 100,
        }
        total_devices_mock.return_value = 500

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 20),
            end=date(2013, 11, 5),
            team=self.team_devices,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices.id)
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 11.76,
                cost_key: _('Incomplete price'),
            },
            self.venture2.id: {
                devices_key: 11.76,
                cost_key: _('Incomplete price'),
            },
            self.venture3.id: {
                devices_key: 5.88,
                cost_key: _('Incomplete price'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_devices_cost_no_price(
        self,
        devices_count_mock,
        total_devices_mock,
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_devices,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        devices_key = 'team_{0}_devices'.format(self.team_devices.id)
        cost_key = 'team_{0}_cost'.format(self.team_devices.id)
        self.assertEquals(result, {
            self.venture1.id: {
                devices_key: 10,
                cost_key: _('No price'),
            },
            self.venture2.id: {
                devices_key: 10,
                cost_key: _('No price'),
            },
            self.venture3.id: {
                devices_key: 20,
                cost_key: _('No price'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_distribute_cost(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 60,
            self.venture3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_distribute,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{0}_cost'.format(self.team_distribute.id)
        # description:
        # costs:
        #   1-15: cost = 3000
        #       members:                    T1       T2       T3       Total
        #       3-10 (cost=8/15*3000=1600): 10(400)  10(400)  20(800)  40(1600)
        #       11-15 (cost=1000)           10(200)  20(400)  20(400)  50(1000)
        #   16-20: cost = 6000
        #       members:
        #       16-20 (cost=1/3*6000=2000)  10(400)  20(800)  20(800)  50(2000)
        #       21-27 (cost=2800)           10(700)  20(1400) 10(700)  40(2800)

        # venture1 (30%, 20%):
        #   3-10:
        #       T1: 0.3 * 400 = 120
        #       T2: 0.25 * 200 + 0.2 * 200 = 90
        #       T3: 0.25 * 800 = 200
        #       Total: 410
        #   11-15:
        #       T1: 0.2 * 200 = 40
        #       T2: 0.25 * 200 + 0.2 * 200 = 90
        #       T3: 0.25 * 400 = 100
        #       Total: 230
        #   16-20:
        #       T1: 0.2 * 400 = 80
        #       T2: 0.25 * 400 + 0.2 * 400 = 180
        #       T3: 0.25 * 800 = 200
        #       Total: 460
        #   21-27:
        #       T1: 0.2 * 700 = 140
        #       T2: 0.25 * 700 + 0.2 * 700 = 315
        #       T3: 0.25 * 700 = 175
        #       Total: 630
        #   total: 1730

        # venture2 (30%, 50%):
        #   3-10:
        #       T1: 0.3 * 400 = 120
        #       T2: 0.25 * 200 + 0.4 * 200 = 130
        #       T3: 0.25 * 800 = 200
        #       Total: 450
        #   11-15:
        #       T1: 0.5 * 200 = 100
        #       T2: 0.25 * 200 + 0.4 * 200 = 130
        #       T3: 0.25 * 400 = 100
        #       Total: 330
        #   16-20:
        #       T1: 0.5 * 400 = 200
        #       T2: 0.25 * 400 + 0.4 * 400 = 260
        #       T3: 0.25 * 800 = 200
        #       Total: 660
        #   21-27:
        #       T1: 0.5 * 700 = 350
        #       T2: 0.25 * 700 + 0.4 * 700 = 455
        #       T3: 0.25 * 700 = 175
        #       Total: 980
        #   total: 2420

        # venture3 (40%, 30%):
        #   3-10:
        #       T1: 0.4 * 400 = 160
        #       T2: 0.5 * 200 + 0.4 * 200 = 180
        #       T3: 0.5 * 800 = 400
        #       Total: 740
        #   11-15:
        #       T1: 0.3 * 200 = 60
        #       T2: 0.5 * 200 + 0.4 * 200 = 180
        #       T3: 0.5 * 400 = 200
        #       Total: 440
        #   16-20:
        #       T1: 0.3 * 400 = 120
        #       T2: 0.5 * 400 + 0.4 * 400 = 360
        #       T3: 0.5 * 800 = 400
        #       Total: 880
        #   21-27:
        #       T1: 0.3 * 700 = 210
        #       T2: 0.5 * 700 + 0.4 * 700 = 630
        #       T3: 0.5 * 700 = 350
        #       Total: 1190
        #   total: 3250

        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('1730'),
            },
            self.venture2.id: {
                cost_key: D('2420'),
            },
            self.venture3.id: {
                cost_key: D('3250'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_distribute_cost_forecast(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 60,
            self.venture3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_distribute,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=True,
            no_price_msg=True,
        )
        cost_key = 'team_{0}_cost'.format(self.team_distribute.id)
        # forecast costs are half of costs
        # detailed calculations in `test_team_distribute_cost`
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('865'),
            },
            self.venture2.id: {
                cost_key: D('1210'),
            },
            self.venture3.id: {
                cost_key: D('1625'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_distribute_cost_incomplete_price(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 60,
            self.venture3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 11, 5),
            team=self.team_distribute,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{0}_cost'.format(self.team_distribute.id)
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
            },
            self.venture3.id: {
                cost_key: _('Incomplete price'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_team_distribute_cost_no_price(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 30,
            self.venture3.id: 60,
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,
            self.venture2.id: 60,
            self.venture3.id: 60,
        }
        total_cores_mock.return_value = 150

        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 11, 3),
            end=date(2013, 11, 5),
            team=self.team_distribute,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'team_{0}_cost'.format(self.team_distribute.id)
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
            },
            self.venture2.id: {
                cost_key: _('No price'),
            },
            self.venture3.id: {
                cost_key: _('No price'),
            },
        })
