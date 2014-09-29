# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cStringIO
from mock import patch, ANY

from django.core.management import call_command
from django.test import TestCase

from ralph_scrooge.management.commands.scrooge_asset_models import Command
from ralph_scrooge.management.commands._scrooge_base import (
    DEFAULT_CSV_ENCODING,
    DEFAULT_ENCODING,
)

# command filename
COMMAND_NAME = Command.__module__.split('.')[-1]


class TestScroogeBaseCommand(TestCase):
    @patch.object(Command, 'get_data', lambda *a, **kw: [['test']])
    def test_get_prepared_data(self):
        self.assertEqual(
            Command().get_prepared_data(),
            [Command.HEADERS, ['test']],
        )

    @patch.object(Command, 'get_data', lambda *a, **kw: [['test']])
    @patch('ralph_scrooge.management.commands._scrooge_base.UnicodeWriter')
    def test_handle_on_screen(self, writer_mock):
        f = cStringIO.StringIO()
        call_command(COMMAND_NAME, stdout=f)
        writer_mock.assert_called_once_with(
            f,
            delimiter=';',
            encoding=DEFAULT_ENCODING,
        )

    @patch.object(Command, 'get_data', lambda *a, **kw: [['test']])
    @patch('ralph_scrooge.management.commands._scrooge_base.UnicodeWriter')
    @patch('__builtin__.open')
    def test_handle_to_file(self, open_mock, writer_mock):
        call_command(COMMAND_NAME, file_path='test_file')
        open_mock.assert_called_once_with('test_file', 'w')
        writer_mock.assert_called_once_with(
            ANY,
            delimiter=';',
            encoding=DEFAULT_CSV_ENCODING,
        )

    @patch.object(
        Command,
        'get_data',
        lambda *a, **kw: [['ĄŚĆŻÓŁŃĘĆ', 'ąśćżółńęć']],
    )
    def test_encoding(self):
        f = cStringIO.StringIO()
        call_command(COMMAND_NAME, stdout=f, encoding='cp1250')
        encoded = map(lambda x: x.encode('cp1250'), [
            ';'.join(Command.HEADERS) + '\r\n',
            ';'.join(['ĄŚĆŻÓŁŃĘĆ', 'ąśćżółńęć']) + '\r\n',
        ])
        # go to beginning of buffer
        f.seek(0)
        self.assertEquals(f.readlines(), encoded)

    def test_help(self):
        self.assertEquals(Command().help, (
            "Generate report with assets and devices matching and basic "
            "information\nabout asset, such as cores count, model name etc."
        ))
