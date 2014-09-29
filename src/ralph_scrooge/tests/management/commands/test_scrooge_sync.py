# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from mock import call, patch

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from ralph.util import plugin
from ralph_scrooge.management.commands import scrooge_sync


COLLECT_PLUGINS = ['asset', 'business_line', 'warehouse']
COMMAND_NAME = scrooge_sync.Command.__module__.split('.')[-1]


class TestScroogeSync(TestCase):
    def test_load_plugins(self):
        scrooge_sync._load_plugins()
        self.assertTrue(scrooge_sync.PLUGINS_LOADED)
        self.assertGreater(len(plugin.BY_NAME.get('scrooge', {})), 0)

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    def test_get_collect_plugins_names(self):
        self.assertEquals(
            scrooge_sync.get_collect_plugins_names(),
            COLLECT_PLUGINS
        )

    @patch('ralph_scrooge.management.commands.scrooge_sync.plugin.run')
    def test_run_plugin(self, plugin_run_mock):
        plugin_run_mock.return_value = True, 'Everything OK'
        today = datetime.date.today()
        scrooge_sync._run_plugin('abc', today)
        plugin_run_mock.assert_called_with('scrooge', 'abc', today=today)

    @patch('ralph_scrooge.management.commands.scrooge_sync.plugin.run')
    def test_run_plugin_failure(self, plugin_run_mock):
        plugin_run_mock.return_value = False, 'Something goes wrong'
        today = datetime.date.today()
        with self.assertRaises(scrooge_sync.PluginError):
            scrooge_sync._run_plugin('abc', today)
        plugin_run_mock.assert_called_with('scrooge', 'abc', today=today)

    @patch('ralph_scrooge.management.commands.scrooge_sync.plugin.run')
    def test_run_plugin_exception(self, plugin_run_mock):
        def side_effect(*args, **kwargs):
            raise Exception('Plugin error')
        plugin_run_mock.side_effect = side_effect
        today = datetime.date.today()
        with self.assertRaises(Exception):
            scrooge_sync._run_plugin('abc', today)
        plugin_run_mock.assert_called_with('scrooge', 'abc', today=today)

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    @patch('ralph_scrooge.management.commands.scrooge_sync._run_plugin')
    def test_run_plugins(self, run_plugin_mock):
        def side_effect(name, today):
            if name == 'business_line':
                raise scrooge_sync.PluginError()
            else:
                return None
        run_plugin_mock.side_effect = side_effect
        today = datetime.date.today()
        result = [r for r in scrooge_sync.run_plugins(
            today,
            COLLECT_PLUGINS + ['abc', 'def']
        )]
        # notice that there is no call for asset plugin, which has not
        # fulfilled dependiencies
        run_plugin_mock.assert_has_calls(
            [
                call('business_line', today),
                call('warehouse', today),
            ],
            any_order=True
        )
        self.assertEquals(set(result), set([
            ('business_line', False),
            ('warehouse', True),
        ]))

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    @patch('ralph_scrooge.management.commands.scrooge_sync.run_plugins')
    def test_command(self, run_plugins_mock):
        run_plugins_mock.iter.return_value.__iter__.return_value = iter([
            ('business_line', False),
            ('warehouse', True),
        ])
        today = datetime.date.today()
        call_command(COMMAND_NAME)
        run_plugins_mock.assert_called_with(today, COLLECT_PLUGINS)

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    @patch('ralph_scrooge.management.commands.scrooge_sync.run_plugins')
    def test_command_today(self, run_plugins_mock):
        run_plugins_mock.iter.return_value.__iter__.return_value = iter([
            ('business_line', False),
            ('warehouse', True),
        ])
        today = datetime.date(2013, 10, 10)
        call_command(COMMAND_NAME, today='2013-10-10')
        run_plugins_mock.assert_called_with(today, COLLECT_PLUGINS)

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    @patch('ralph_scrooge.management.commands.scrooge_sync.run_plugins')
    def test_command_yesterday(self, run_plugins_mock):
        run_plugins_mock.iter.return_value.__iter__.return_value = iter([
            ('business_line', False),
            ('warehouse', True),
        ])
        yesterday = datetime.date(2013, 10, 10)
        call_command(COMMAND_NAME, today='2013-10-11', yesterday=True)
        run_plugins_mock.assert_called_with(yesterday, COLLECT_PLUGINS)

    @override_settings(COLLECT_PLUGINS=COLLECT_PLUGINS)
    @patch('ralph_scrooge.management.commands.scrooge_sync.run_plugins')
    def test_command_run_only(self, run_plugins_mock):
        run_plugins_mock.iter.return_value.__iter__.return_value = iter([
            ('business_line', False),
        ])
        today = datetime.date.today()
        call_command(COMMAND_NAME, run_only='business_line')
        run_plugins_mock.assert_called_with(
            today,
            ['business_line'],
            run_only=True
        )
