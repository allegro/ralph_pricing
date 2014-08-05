# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import MagicMock, patch

from django.test import TestCase
from django.conf import settings

from ralph_scrooge.models import (
    UsageType,
    DailyUsage,
    PricingObjectType,
)
from ralph_scrooge.plugins.collect import netflow
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    DailyPricingObjectFactory,
    ServiceFactory,
)


class SshClientMock():
    def __init__(self, stdin='', stdout='', stderr=''):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def exec_command(self, command):
        return (
            MagicMock(read=MagicMock(return_value=self.stdin)),
            MagicMock(
                read=MagicMock(return_value=self.stdout),
                readlines=MagicMock(return_value=self.stdout),
            ),
            MagicMock(read=MagicMock(return_value=self.stderr)),
        )


def get_ssh_client_mock(address, login, password):
    return SshClientMock(
        stdout=[
            '',
            '10.10.10.10 | 20.20.20.20 | 30',
            '',
            '',
            '',
            '',
        ],
    )


class TestNetwork(TestCase):
    def setUp(self):
        settings.NFSEN_CLASS_ADDRESS = []
        settings.SSH_NFSEN_CREDENTIALS = {}
        settings.NFSEN_CHANNELS = []
        settings.NETWORK_UNKNOWN_VENTURE_SYMBOL = ''

    def test_get_names_of_data_files_when_executed_commend_return_error(self):
        self.assertRaises(
            netflow.RemoteServerError,
            netflow.get_names_of_data_files,
            ssh_client=SshClientMock(stderr='error'),
            channel='test-channel',
            date='2014-10-01',
        )

    def test_get_names_of_data_files(self):
        self.assertEqual(
            netflow.get_names_of_data_files(
                SshClientMock(stdout=['1\n', '2']),
                'test-channel',
                '2014-10-01',
            ),
            [u'1', u'2'],
        )

    def test_execute_nfdump(self):
        self.assertEqual(
            netflow.execute_nfdump(
                SshClientMock(stdout=['0', '1', '2', '3', '4', '5', '6']),
                'test-channel',
                '2014-10-01',
                ['file1', 'file2'],
                'scrip',
            ),
            [u'1', u'2'],
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_extract_ip_and_bytes_when_input_output_is_scrip(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 30',
                'scrip',
            ),
            (u'10.10.10.10', 30)
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['20.20.20.20'])
    def test_extract_ip_and_bytes_when_input_output_is_dstip(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 30',
                'dstip',
            ),
            (u'20.20.20.20', 30),
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_bytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 3000',
                'scrip',
            )[1],
            3000
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_megabytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 1 M',
                'scrip',
            )[1],
            1048576
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_gigabytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 1 G',
                'scrip',
            )[1],
            1073741824
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_incorrect_format(self):
        self.assertRaises(
            netflow.UnknowDataFormatError,
            netflow.extract_ip_and_bytes,
            row='10.10.10.10 | 20.20.20.20 | 1 X',
            input_output='scrip',
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['30.30.30.30'])
    def test_extract_ip_and_bytes_when_ip_is_not_in_class_address(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 30',
                'scrip',
            ),
            None
        )

    def test_get_network_usage_when_ip_and_byte_is_none(self):
        self.assertEqual(
            netflow.get_network_usage(
                SshClientMock(
                    stdout=[
                        '',
                        '10.10.10.10 | 20.20.20.20 | 30',
                        '',
                        '',
                        '',
                        '',
                    ],
                ),
                'test-channel',
                '2014-10-01',
                ['file1', 'file2'],
                'scrip',
            ),
            {}
        )

    @patch.object(settings, 'NFSEN_CLASS_ADDRESS', ['10.10.10.10'])
    def test_get_network_usage(self):
        self.assertEqual(
            netflow.get_network_usage(
                SshClientMock(
                    stdout=[
                        '',
                        '10.10.10.10 | 20.20.20.20 | 30',
                        '',
                        '',
                        '',
                        '',
                    ],
                ),
                'test-channel',
                '2014-10-01',
                ['file1', 'file2'],
                'scrip',
            ),
            {u'10.10.10.10': 30}
        )

    @patch.object(
        settings,
        'NFSEN_CLASS_ADDRESS',
        ['10.10.10.10', '20.20.20.20'],
    )
    @patch.object(
        settings,
        'SSH_NFSEN_CREDENTIALS', {
            'address': {
                'login': 'login',
                'password': 'password',
            },
        },
    )
    @patch.object(netflow, 'get_ssh_client', get_ssh_client_mock)
    @patch.object(settings, 'NFSEN_CHANNELS', ['test-channel'])
    def test_get_network_usages(self):
        self.assertEqual(
            netflow.get_network_usages('2014-10-01'),
            {u'20.20.20.20': 30, u'10.10.10.10': 30},
        )

    def test_get_usages_type(self):
        self.assertEqual(netflow.get_usage_type(), UsageType.objects.get())

    def test_get_pricing_objects_and_ips(self):
        pricing_object = PricingObjectFactory.create(
            name='8.8.8.8',
            type=PricingObjectType.ip_address,
        )
        self.assertEqual(
            netflow.get_pricing_objects_and_ips(
                date(
                    year=2014,
                    month=1,
                    day=1,
                )
            ),
            {'8.8.8.8': pricing_object.daily_pricing_objects.all()[0]}
        )

    @patch.object(settings, 'UNKNOWN_SERVICES', {'network': 1})
    def test_update_when_pricing_object_does_not_exist(self):
        ServiceFactory.create(ci_uid=1)
        self.assertEqual(
            netflow.update(
                {'8.8.8.8': 10},
                {},
                netflow.get_usage_type(),
                date(year=2014, month=1, day=1),
            ),
            (1, 0, 1)
        )

    @patch.object(settings, 'UNKNOWN_SERVICES', {'network': 1})
    def test_update(self):
        pricing_object = PricingObjectFactory.create(
            name='8.8.8.8',
            type=PricingObjectType.ip_address,
        )
        daily_pricing_object = DailyPricingObjectFactory.create(
            pricing_object=pricing_object,
        )
        ServiceFactory.create(ci_uid=1)
        self.assertEqual(
            netflow.update(
                {'8.8.8.8': 30},
                {'8.8.8.8': daily_pricing_object},
                netflow.get_usage_type(),
                date(year=2014, month=1, day=1),
            ),
            (0, 1, 1)
        )

    @patch.object(
        settings,
        'NFSEN_CLASS_ADDRESS',
        ['10.10.10.10'],
    )
    @patch.object(
        settings,
        'SSH_NFSEN_CREDENTIALS', {
            'address': {
                'login': 'login',
                'password': 'password',
            },
        },
    )
    @patch.object(settings, 'NFSEN_CHANNELS', ['test-channel'])
    @patch.object(netflow, 'get_ssh_client', get_ssh_client_mock)
    @patch.object(settings, 'UNKNOWN_SERVICES', {'network': 1})
    def test_network(self):
        ServiceFactory.create(ci_uid=1)
        self.assertEqual(
            netflow.netflow(today=date(year=2014, month=1, day=1))[1],
            '1 new, 0 updated, 1 total',
        )
        self.assertEqual(DailyUsage.objects.get().value, 30)
