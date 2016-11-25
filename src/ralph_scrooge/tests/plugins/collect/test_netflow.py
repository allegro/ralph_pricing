# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import MagicMock, patch

from django.conf import settings
from django.test.utils import override_settings

from ralph_scrooge.models import (
    DailyUsage,
    PRICING_OBJECT_TYPES,
    UsageType,
)
from ralph_scrooge.plugins.collect import netflow
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    DailyPricingObjectFactory,
    IPInfoFactory,
    ServiceEnvironmentFactory,
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
            '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 30',
            '',
            '',
            '',
            '',
        ],
    )


class TestNetwork(ScroogeTestCase):
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
                'srcip',
                settings.NFSEN_CLASS_ADDRESS,
            ),
            [u'1', u'2'],
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_input_output_is_srcip(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 30',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            (u'10.10.10.10', '80', 30)
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['20.20.20.20'])
    def test_extract_ip_and_bytes_when_input_output_is_dstip(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 30',
                ['dst', 'dstip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            (u'20.20.20.20', '443', 30),
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_bytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 3000',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            )[-1],
            3000
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_megabytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 1 M',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            )[-1],
            1048576
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_gigabytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 1 G',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            )[-1],
            1073741824
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_terabytes_format(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 1 T',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            )[-1],
            1099511627776
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_extract_ip_and_bytes_when_bytes_string_is_incorrect_format(self):
        self.assertRaises(
            netflow.UnknowDataFormatError,
            netflow.extract_ip_and_bytes,
            row='10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 1 X',
            input_output=['src', 'srcip'],
            class_addresses=settings.NFSEN_CLASS_ADDRESS,
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['30.30.30.30'])
    def test_extract_ip_and_bytes_when_ip_is_not_in_class_address(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 30',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            None
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['2001:db8::1428:0/112'])
    def test_extract_ip_and_bytes_for_ipv6(self):
        self.assertEqual(
            netflow.extract_ip_and_bytes(
                '2001:db8::1428:57ab | 20.20.20.20 | 80 | 443 | tcp | 30',
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            (u'2001:db8::1428:57ab', '80', 30),
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
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            {}
        )

    @override_settings(NFSEN_CLASS_ADDRESS=['10.10.10.10'])
    def test_get_network_usage(self):
        self.assertEqual(
            netflow.get_network_usage(
                SshClientMock(
                    stdout=[
                        '',
                        '10.10.10.10 | 20.20.20.20 | 80 | 443 | tcp | 30',
                        '',
                        '',
                        '',
                        '',
                    ],
                ),
                'test-channel',
                '2014-10-01',
                ['file1', 'file2'],
                ['src', 'srcip'],
                settings.NFSEN_CLASS_ADDRESS,
            ),
            {('10.10.10.10', '80'): 30}
        )

    @patch.object(netflow, 'get_ssh_client', get_ssh_client_mock)
    @override_settings(
        UNKNOWN_SERVICES={'netflow': 1},
        NFSEN_CHANNELS=['test-channel'],
        SSH_NFSEN_CREDENTIALS={
            'address': {
                'login': 'login',
                'password': 'password',
            },
        },
        NFSEN_CLASS_ADDRESS=['10.10.10.10', '20.20.20.20'],
    )
    def test_get_network_usages(self):
        self.assertEqual(
            netflow.get_network_usages(
                '2014-10-01',
                settings.NFSEN_CLASS_ADDRESS
            ),
            {('20.20.20.20', '443'): 30, ('10.10.10.10', '80'): 30},
        )

    def test_get_usages_type(self):
        self.assertEqual(
            netflow.get_usage_type(),
            UsageType.objects_admin.get()
        )

    @override_settings(UNKNOWN_SERVICES={'netflow': 1}, NFSEN_MIN_VALUE=10)
    def test_update(self):
        service_environment = ServiceEnvironmentFactory()
        pricing_object = IPInfoFactory.create(
            name='8.8.8.8',
            type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
            service_environment=service_environment,
        )
        DailyPricingObjectFactory.create(
            pricing_object=pricing_object,
            service_environment=service_environment,
        )
        self.assertEqual(
            netflow.update(
                {('8.8.8.8', '80'): 30, ('1.2.3.4', '443'): 5},
                netflow.get_usage_type(),
                service_environment,
                date(year=2014, month=1, day=1),
            ),
            (0, 1, 1)
        )

    @patch.object(netflow, 'get_ssh_client', get_ssh_client_mock)
    @override_settings(
        UNKNOWN_SERVICES_ENVIRONMENTS={'netflow': (1, 'env1')},
        NFSEN_CHANNELS=['test-channel'],
        SSH_NFSEN_CREDENTIALS={
            'address': {
                'login': 'login',
                'password': 'password',
            },
        },
        NFSEN_CLASS_ADDRESS=['10.10.10.10'],
    )
    def test_network(self):
        ServiceEnvironmentFactory.create(
            service__ci_uid=1,
            environment__name='env1'
        )
        self.assertEqual(
            netflow.netflow(today=date(year=2014, month=1, day=1))[1],
            '1 new, 0 updated, 1 total',
        )
        self.assertEqual(DailyUsage.objects.get().value, 30)
