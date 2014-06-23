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

from ralph_pricing import models
from ralph_pricing.plugins.reports.team import Team


class TestTeamPlugin(TestCase):
    def tearDown(self):
        # set up decimal precision to make comparisons easier
        decimal_context = getcontext()
        decimal_context.prec = self.__prev_decimal_prec

    def setUp(self):
        # set up decimal precision to make comparisons easier
        decimal_context = getcontext()
        self.__prev_decimal_prec = decimal_context.prec
        decimal_context.prec = 4

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
            show_percent_column=True,
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

        # dateranges
        self.daterange1 = models.TeamDaterange(
            team=self.team_time,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
        )
        self.daterange1.save()
        self.daterange2 = models.TeamDaterange(
            team=self.team_time,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
        )
        self.daterange2.save()

        # costs
        # team time
        up = models.UsagePrice(
            type=self.usage_type,
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_time,
            team_members_count=10,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=900,
            forecast_cost=450,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_time,
            team_members_count=20,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=300,
            forecast_cost=600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 30),
            team=self.team_devices_cores,
            team_members_count=20,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=800,
            forecast_cost=1600,
            start=date(2013, 10, 1),
            end=date(2013, 10, 10),
            team=self.team_devices,
            team_members_count=20,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=100,
            forecast_cost=200,
            start=date(2013, 10, 11),
            end=date(2013, 10, 30),
            team=self.team_devices,
            team_members_count=10,
        )
        up.save()

        up = models.UsagePrice(
            type=self.usage_type,
            cost=3000,
            forecast_cost=1500,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=self.team_distribute,
            team_members_count=10,
        )
        up.save()
        up = models.UsagePrice(
            type=self.usage_type,
            cost=6000,
            forecast_cost=3000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=self.team_distribute,
            team_members_count=10,
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
            (self.daterange1, [30, 30, 40]),
            (self.daterange2, [20, 50, 30]),
        )
        for team_daterange, percent in percentage:
            for venture, p in zip(self.ventures, percent):
                tvp = models.TeamVenturePercent(
                    team_daterange=team_daterange,
                    venture=venture,
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
                self.team_devices_cores.id: 20,
                self.team_devices.id: 20,
                self.team_distribute.id: 10,
            },
            (date(2013, 10, 11), date(2013, 10, 15)): {
                self.team_time.id: 10,
                self.team_devices_cores.id: 20,
                self.team_devices.id: 10,
                self.team_distribute.id: 10,
            },
            (date(2013, 10, 16), date(2013, 10, 27)): {
                self.team_time.id: 20,
                self.team_devices_cores.id: 20,
                self.team_devices.id: 10,
                self.team_distribute.id: 10,
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('212'),
                percent_key: D('0.2163'),
            },
            self.venture2.id: {
                cost_key: D('458'),
                percent_key: D('0.4673'),
            },
            self.venture3.id: {
                cost_key: D('310'),
                percent_key: D('0.3163'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture3.id: {
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
        for venture, percent in zip(self.ventures, [30, 20, 50]):
            tvp = models.TeamVenturePercent(
                team_daterange=daterange,
                venture=venture,
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_time.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('208'),
                percent_key: D('0.2364'),
            },
            self.venture2.id: {
                cost_key: D('376'),
                percent_key: D('0.4273'),
            },
            self.venture3.id: {
                cost_key: D('296'),
                percent_key: D('0.3364'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        # cost (1-30): 300
        # cost (3-27): 250
        # daily cost: 250 / 25 = 10
        # devices cost in period: 10 * 25 / 2 = 125
        # cores cost in period: 10 * 25 / 2 = 125
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
                percent_key: D('0.3'),
            },
            self.venture2.id: {
                cost_key: D('100'),  # 0.4 * 125 + 0.4 * 125
                percent_key: D('0.4'),
            },
            self.venture3.id: {
                cost_key: D('75'),  # 0.4 * 125 + 0.2 * 125
                percent_key: D('0.3'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        # forecast (1-30): 600
        # forecast (3-27): 500
        # daily cost: 500 / 25 = 20
        # devices cost in period: 20 * 25 / 2 = 250
        # cores cost in period: 20 * 25 / 2 = 250
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
                percent_key: D('0.3'),
            },
            self.venture2.id: {
                cost_key: D('200'),  # 0.4 * 250 + 0.4 * 250
                percent_key: D('0.4'),
            },
            self.venture3.id: {
                cost_key: D('150'),  # 0.4 * 250 + 0.2 * 250
                percent_key: D('0.3'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices_cores.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
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
            self.venture1.id: 200,
            self.venture2.id: 200,
            self.venture3.id: 100,
        }
        total_devices_mock.return_value = 500
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            team=self.team_devices,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
        )
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        # cost (1-10): 800
        # cost (11-30): 100
        # devices daily cost (1-10): 800 / 10 = 80
        # devices daily cost (11-30): 100 / 20 = 5
        # devices cost in period: (3-10): 8 / 10 * 800 = 640
        # devices cost in period: (11-27): 17 / 20 * 100 = 85
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('290'),  # 0.4 * 640 + 0.4 * 85
                percent_key: D('0.4'),
            },
            self.venture2.id: {
                cost_key: D('290'),  # 0.4 * 640 + 0.4 * 85
                percent_key: D('0.4'),
            },
            self.venture3.id: {
                cost_key: D('145'),  # 0.2 * 640 + 0.2 * 85
                percent_key: D('0.2'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        # cost (1-10): 1600
        # cost (11-30): 200
        # devices daily cost (1-10): 1600 / 10 = 160
        # devices daily cost (11-30): 200 / 20 = 10
        # devices cost in period: (3-10): 8 / 10 * 1600 = 1280
        # devices cost in period: (11-27): 17 / 20 * 200 = 170
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('145'),  # 0.1 * 1280 + 0.1 * 170
                percent_key: D('0.1'),
            },
            self.venture2.id: {
                cost_key: D('870'),  # 0.6 * 1280 + 0.6 * 170
                percent_key: D('0.6'),
            },
            self.venture3.id: {
                cost_key: D('435'),  # 0.3 * 1280 + 0.3 * 170
                percent_key: D('0.3'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_devices.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
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
            self.venture1.id: 30,  # 25%
            self.venture2.id: 30,  # 25%
            self.venture3.id: 60,  # 50%
        }
        total_devices_mock.return_value = 120
        cores_count_mock.return_value = {
            self.venture1.id: 30,  # 20%
            self.venture2.id: 60,  # 40%
            self.venture3.id: 60,  # 40%
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        # description:
        # costs:
        #   1-15: cost = 3000
        #     members:                    Team1    Team2    Team3    Total
        #     3-10 (cost=8/15*3000=1600): 10(320)  20(640)  20(640)  50(1600)
        #     11-15 (cost=1000)           10(250)  20(500)  10(250)  40(1000)
        #   16-30: cost = 6000
        #     members:
        #     16-27 (cost=4/5*6000=4800)  20(1920)  20(1920)  10(960)  50(4800)

        # venture1 (30%, 20%):
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

        # venture2 (30%, 50%):
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

        # venture3 (40%, 30%):
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
            self.venture1.id: {
                cost_key: D('1680'),
                percent_key: D('0.2270'),
            },
            self.venture2.id: {
                cost_key: D('2638'),
                percent_key: D('0.3565'),
            },
            self.venture3.id: {
                cost_key: D('3081'),
                percent_key: D('0.4164'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        # forecast costs are half of costs
        # detailed calculations in `test_team_distribute_cost`
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('840.4'),
                percent_key: D('0.2271'),
            },
            self.venture2.id: {
                cost_key: D('1318'),
                percent_key: D('0.3562'),
            },
            self.venture3.id: {
                cost_key: D('1540'),
                percent_key: D('0.4162'),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            self.team_distribute.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_team_time_cost_per_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_team_devices_cores_cost_per_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_team_devices_cost_per_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_team_distributed_cost_per_venture')  # noqa
    def test_team_average_cost(
        self,
        distributed_mock,
        devices_mock,
        devices_cores_mock,
        time_team_mock,
    ):
        team_avg = models.Team(name='TeamAVG', billing_type='AVERAGE')
        team_avg.save()
        team_percent_key = lambda t: 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            t.id,
        )

        time_percent_key = team_percent_key(self.team_time)
        time_team_mock.return_value = {
            self.venture1.id: {time_percent_key: D('0.3')},
            self.venture2.id: {time_percent_key: D('0.3')},
            self.venture3.id: {time_percent_key: D('0.4')},
        }

        devices_cores_percent_key = team_percent_key(self.team_devices_cores)
        devices_cores_mock.return_value = {
            self.venture1.id: {devices_cores_percent_key: 0},
            self.venture2.id: {devices_cores_percent_key: 0},
        }

        devices_percent_key = team_percent_key(self.team_devices)
        devices_mock.return_value = {
            self.venture1.id: {devices_percent_key: D('0.1')},
            self.venture2.id: {devices_percent_key: D('0.3')},
            self.venture3.id: {devices_percent_key: D('0.6')},
        }

        distribted_percent_key = team_percent_key(self.team_distribute)
        distributed_mock.return_value = {
            self.venture2.id: {distribted_percent_key: D('0.3')},
            self.venture3.id: {distribted_percent_key: D('0.7')},
        }

        # daily cost: 100
        up = models.UsagePrice(
            type=self.usage_type,
            cost=1500,
            forecast_cost=2000,
            start=date(2013, 10, 1),
            end=date(2013, 10, 15),
            team=team_avg,
        )
        up.save()
        # daily cost: 200
        up = models.UsagePrice(
            type=self.usage_type,
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        up.save()
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 6),
            end=date(2013, 10, 25),
            team=team_avg,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            team_avg.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            team_avg.id,
        )
        # venture1: 0.3 + 0 + 0.1 = 0.4
        # venture2: 0.3 + 0 + 0.3 + 0.3 = 0.9
        # venture3: 0.4 + 0.6 + 0.7 = 1.7
        # cost between 6 and 15: 100 * 10 = 1000
        # cost between 16 and 25: 200 * 10 = 2000
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: D('400'),  # 1000 * 0.4 / 3 + 2000 * 0.4 / 3
                percent_key: D('0.1333'),  # 400 / 3000
            },
            self.venture2.id: {
                cost_key: D('900'),  # 1000 * 0.9 / 3 + 2000 * 0.9 / 3
                percent_key: D('0.3'),  # 900 / 3000
            },
            self.venture3.id: {
                cost_key: D('1700'),  # 1000 * 1.7 / 3 + 2000 * 1.7 / 3
                percent_key: D('0.5667'),  # 1700 / 3000
            },
        })

    def test_team_average_cost_incomplete_price(self):
        team_avg = models.Team(name='TeamAVG', billing_type='AVERAGE')
        team_avg.save()
        # daily cost: 200
        up = models.UsagePrice(
            type=self.usage_type,
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        up.save()
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 10, 25),
            end=date(2013, 11, 5),
            team=team_avg,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            team_avg.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            team_avg.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('Incomplete price'),
                percent_key: D(0),
            },
        })

    def test_team_average_cost_no_price(self):
        team_avg = models.Team(name='TeamAVG', billing_type='AVERAGE')
        team_avg.save()
        # daily cost: 200
        up = models.UsagePrice(
            type=self.usage_type,
            cost=3000,
            forecast_cost=5000,
            start=date(2013, 10, 16),
            end=date(2013, 10, 30),
            team=team_avg,
        )
        up.save()
        result = self.plugin._get_team_cost_per_venture(
            start=date(2013, 11, 2),
            end=date(2013, 11, 5),
            team=team_avg,
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        cost_key = 'ut_{0}_team_{1}_cost'.format(
            self.usage_type.id,
            team_avg.id,
        )
        percent_key = 'ut_{0}_team_{1}_percent'.format(
            self.usage_type.id,
            team_avg.id,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture2.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
            self.venture3.id: {
                cost_key: _('No price'),
                percent_key: D(0),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_usages(
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
        result = self.plugin.costs(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            usage_type=self.usage_type,
            ventures=self.ventures,
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                'ut_1_team_1_cost': D('212'),
                'ut_1_team_1_percent': D('0.2163'),
                'ut_1_team_2_cost': D('75'),
                'ut_1_team_2_percent': D('0.3'),
                'ut_1_team_3_cost': D('290'),
                'ut_1_team_3_percent': D('0.4'),
                'ut_1_team_4_cost': D('2188'),
                'ut_1_team_4_percent': D('0.2957'),
                'ut_1_total_cost': D('2765'),
            },
            self.venture2.id: {
                'ut_1_team_1_cost': D('458'),
                'ut_1_team_1_percent': D('0.4673'),
                'ut_1_team_2_cost': D('100'),
                'ut_1_team_2_percent': D('0.4'),
                'ut_1_team_3_cost': D('290'),
                'ut_1_team_3_percent': D('0.4'),
                'ut_1_team_4_cost': D('3145'),
                'ut_1_team_4_percent': D('0.425'),
                'ut_1_total_cost': D('3993'),
            },
            self.venture3.id: {
                'ut_1_team_1_cost': D('310'),
                'ut_1_team_1_percent': D('0.3163'),
                'ut_1_team_2_cost': D('75'),
                'ut_1_team_2_percent': D('0.3'),
                'ut_1_team_3_cost': D('145'),
                'ut_1_team_3_percent': D('0.2'),
                'ut_1_team_4_cost': D('2067'),
                'ut_1_team_4_percent': D('0.2793'),
                'ut_1_total_cost': D('2597'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_usages_subventures(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
        }
        total_devices_mock.return_value = 500
        cores_count_mock.return_value = {
            self.venture1.id: 20,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.costs(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            usage_type=self.usage_type,
            ventures=[self.venture1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                'ut_1_team_1_cost': D('212'),
                'ut_1_team_1_percent': D('0.2163'),
                'ut_1_team_2_cost': D('75'),
                'ut_1_team_2_percent': D('0.3'),
                'ut_1_team_3_cost': D('290'),
                'ut_1_team_3_percent': D('0.4'),
                'ut_1_team_4_cost': D('2188'),
                'ut_1_team_4_percent': D('0.2957'),
                'ut_1_total_cost': D('2765'),
            },
        })

    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_cores_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_cores_count_by_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_total_devices_count')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.team.Team._get_devices_count_by_venture')  # noqa
    def test_total_cost(
        self,
        devices_count_mock,
        total_devices_mock,
        cores_count_mock,
        total_cores_mock
    ):
        devices_count_mock.return_value = {
            self.venture1.id: 200,
        }
        total_devices_mock.return_value = 500
        cores_count_mock.return_value = {
            self.venture1.id: 20,
        }
        total_cores_mock.return_value = 100
        result = self.plugin.total_cost(
            start=date(2013, 10, 3),
            end=date(2013, 10, 27),
            usage_type=self.usage_type,
            ventures=[self.venture1],
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, D('2765'))

    def test_exclude_ventures(self):
        self.team_time.excluded_ventures.add(self.venture1)
        result = self.plugin._exclude_ventures(self.team_time, self.ventures)
        self.assertEquals(set(result), {self.venture2, self.venture3})

    def test_exclude_ventures_empty(self):
        result = self.plugin._exclude_ventures(self.team_time, self.ventures)
        self.assertEquals(result, self.ventures)

    def test_schema(self):
        result = self.plugin.schema(self.usage_type)
        ut_id = self.usage_type.id
        self.assertEquals(result, OrderedDict([
            ('ut_{0}_team_{1}_percent'.format(ut_id, self.team_time.id), {
                'name': _("{0} - {1} %".format(
                    self.usage_type.name,
                    self.team_time.name,
                )),
                'rounding': 4,
            }),
            ('ut_{0}_team_{1}_cost'.format(ut_id, self.team_time.id), {
                'name': _("{0} - {1} cost".format(
                    self.usage_type.name,
                    self.team_time.name,
                )),
                'currency': True,
                'total_cost': False,
            }),
            ('ut_{0}_team_{1}_cost'.format(
                ut_id,
                self.team_devices_cores.id
                ), {
                'name': _("{0} - {1} cost".format(
                    self.usage_type.name,
                    self.team_devices_cores.name,
                )),
                'currency': True,
                'total_cost': False,
            }),
            ('ut_{0}_team_{1}_cost'.format(ut_id, self.team_devices.id), {
                'name': _("{0} - {1} cost".format(
                    self.usage_type.name,
                    self.team_devices.name,
                )),
                'currency': True,
                'total_cost': False,
            }),
            ('ut_{0}_team_{1}_cost'.format(ut_id, self.team_distribute.id), {
                'name': _("{0} - {1} cost".format(
                    self.usage_type.name,
                    self.team_distribute.name,
                )),
                'currency': True,
                'total_cost': False,
            }),
            ('ut_{0}_total_cost'.format(ut_id), {
                'name': _("{0} total cost".format(
                    self.usage_type.name,
                )),
                'currency': True,
                'total_cost': True,
            }),
        ]))
