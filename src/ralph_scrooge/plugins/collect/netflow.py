# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import ipaddr
from collections import defaultdict

import paramiko
from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.models import (
    UsageType,
    Service,
    DailyUsage,
    PricingObject,
    PricingObjectType,
    DailyPricingObject,
)


logger = logging.getLogger(__name__)


class UnknowDataFormatError(Exception):
    """
    Raise this exception when data contains any different format like except
    """
    pass


class RemoteServerError(Exception):
    """
    Raise this exception when command executed on remote server trigger the
    error
    """
    pass


class ServiceDoesNotExistError(Exception):
    """
    Raise this exception when service does not exist
    """
    pass


def get_ssh_client(address, login, password):
    """
    Create ssh client and connect them to give address by using given
    credentials

    :param string address: Remote server address
    :param string login: User name to remote server
    :param string login: Password to remote server
    :returns object: ssh client with connection to remote server
    :rtype object:
    """
    logger.debug(
        'Client {0} {1} ****'.format(
            address,
            login,
            password,
        )
    )
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(address, username=login, password=password)
    return ssh_client


def get_names_of_data_files(ssh_client, channel, date):
    """
    Generate list of file names from given channel and date. Execute
    simple ls on remote server in correct folder

    :param object ssh_client: Client connected to the remote server
    :param string channel: Channel name from which usages will be collects
    :param datetime date: Date for which usages will collects
    :returns list: list of file names
    :rtype list:
    """
    split_date = str(date).split('-')
    stdin, stdout, stderr = ssh_client.exec_command(
        "ls {0}/{1}/{2}/{3}/{4}/".format(
            settings.NFSEN_FILES_PATH,
            channel,
            split_date[0],
            split_date[1],
            split_date[2],
        ),
    )
    if stderr.read():
        raise RemoteServerError(stderr.read())
    return sorted([row.strip('\n') for row in stdout.readlines()])


def execute_nfdump(ssh_client, channel, date, file_names, input_output):
    """
    Collects data by executing correct nfdump command on remote server

    :param object ssh_client: Client connected to the remote server
    :param string channel: Channel name from which usages will be collects
    :param datetime date: Date for which usages will collects
    :param list file_names: List with file names from remote server. This
    files contains trafic statistics.
    :param string input_output: Define direct of trafic (srcip or dstip)
    :returns list: list of rows from stdout from remote server
    :rtype list:
    """
    def get_networks(input_output):
        direct = input_output.replace('ip', '')
        networks = []
        for class_address in settings.NFSEN_CLASS_ADDRESS:
            networks.append('{0} net '.format(direct) + class_address)
        return ' or '.join(networks)

    split_date = str(date).split('-')
    nfdump_str = "nfdump -M {0}/{1}"\
        " -T -R {2}/{3}/{4}/{5}:{2}/{3}/{4}/{6} -o "\
        "\"fmt:%sa | %da | %byt\" -a -A {7} '{8}';exit".format(
            settings.NFSEN_FILES_PATH,
            channel,
            split_date[0],
            split_date[1],
            split_date[2],
            file_names[0],
            file_names[-1],
            input_output,
            get_networks(input_output)
        )
    logger.debug(nfdump_str)
    stdin, stdout, stderr = ssh_client.exec_command(nfdump_str)
    return stdout.readlines()[1:-4]


def extract_ip_and_bytes(row, input_output):
    """
    Extract/process ip address and usage in bytes from string. String is taken
    from executing nfdump commend on remote server and looks like:

    'srcip_ip_address | dstip_ip_address | usage_in_bytes'

    :param string row: Single row gain from remote server by execute nfdump
    commands
    :param string input_output: Define which address will be take
    :returns tuple: Pair ip_address with usage in bytes or None
    :rtype tuple:
    """
    def unification(bytes_string):
        bytes_list = bytes_string.split(' ')
        # there is no K option becouse KB is wrote like a bytes by nfdump
        if len(bytes_list) == 1:
            return int(bytes_list[0])
        elif bytes_list[1] == 'M':
            return int(float(bytes_list[0]) * 1048576)
        elif bytes_list[1] == 'G':
            return int(float(bytes_list[0]) * 1073741824)
        else:
            raise UnknowDataFormatError(
                'Data cannot be unificated. Unknow field format'
                ' \'{0} {1}\''.format(
                    bytes_list[0],
                    bytes_list[1],
                )
            )

    split_row = [cell.replace('\x01', '').strip() for cell in row.split('|')]
    ip_address = split_row[0]
    if input_output == 'dstip':
        ip_address = split_row[1]

    for class_address in settings.NFSEN_CLASS_ADDRESS:
        if ipaddr.IPv4Address(ip_address) in ipaddr.IPv4Network(class_address):
            return (ip_address, unification(split_row[2]))


def get_network_usage(ssh_client, channel, date, file_names, input_output):
    """
    Collect usages for given channel, date and input/output. Used by
    get_network_usages method. Returned data struct looks like:

    returned_data = {
        'ip_address': 'usage_in_bytes',
        ...
    }

    :param object ssh_client: Client connected to the remote server
    :param string channel: Channel name from which usages will be collects
    :param datetime date: Date for which usages will collects
    :param list file_names: List with file names from remote server. This
    files contains trafic statistics.
    :param string input_output: Define direct of trafic (srcip or dstip)
    :returns dict: list of ips with usages from given date
    :rtype dict:
    """
    ip_and_bytes = defaultdict(int)
    for row in execute_nfdump(
        ssh_client,
        channel,
        date,
        file_names,
        input_output,
    ):
        ip_and_byte = extract_ip_and_bytes(row, input_output)
        if ip_and_byte:
            ip_and_bytes[ip_and_byte[0]] += ip_and_byte[1]
    return ip_and_bytes


def get_network_usages(date):
    """
    Based on settings, collect data from remote server. Returned data struct
    looks like:

    returned_data = {
        'ip_address': 'usage_in_bytes',
        ...
    }

    :param datetime date: Date for which usages will collects
    :returns dict: list of ips with usages from given date
    :rtype dict:
    """
    logger.debug('Getting network usages per IP')
    network_usages = defaultdict(int)
    for address, credentials in settings.SSH_NFSEN_CREDENTIALS.iteritems():
        ssh_client = get_ssh_client(address, **credentials)
        for channel in settings.NFSEN_CHANNELS:
            for input_output in ['srcip', 'dstip']:
                logger.debug("Server:{0} Channel:{1} I/O:{2}".format(
                    address, channel, input_output))
                for ip, value in get_network_usage(
                    ssh_client,
                    channel,
                    date,
                    get_names_of_data_files(ssh_client, channel, date),
                    input_output,
                ).iteritems():
                    network_usages[ip] += value
    return network_usages


def get_usage_type():
    """
    Creates network usage type if not created

    :returns object: Network Bytes usage type
    :rtype object:
    """
    usage_type, created = UsageType.objects.get_or_create(
        name="Network Bytes",
        symbol='network_bytes',
    )
    return usage_type


def update(
    network_usages,
    usage_type,
    default_service,
    date,
):
    """
    Create or update daily usage

    :param dict network_usages: Usages per IP
    :param object usage_type: UsageType object
    :param datetime date: Date for which dailyusage will be update
    :returns list: new update and total counts
    :rtype list:
    """
    logger.debug('Saving usages as a daily usages per service')
    new = updated = total = 0

    for ip, value in network_usages.iteritems():
        total += 1
        pricing_object, created = PricingObject.objects.get_or_create(
            name=ip,
            type=PricingObjectType.ip_address,
            defaults=dict(
                service=default_service,
            )
        )
        daily_pricing_object = DailyPricingObject.objects.get_or_create(
            date=date,
            pricing_object=pricing_object,
            defaults=dict(
                service=default_service,
            )
        )[0]
        daily_usage, usage_created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            daily_pricing_object=daily_pricing_object,
            defaults=dict(
                service=daily_pricing_object.service,
            ),
        )
        daily_usage.service = daily_pricing_object.service
        daily_usage.value = value
        daily_usage.save()
        if created:
            logger.warning(
                'Unknown ip address {} (usage: {})'.format(ip, value)
            )
        new += created
        updated += not created
    return (new, updated, total)


@plugin.register(chain='scrooge', requires=['service'])
def netflow(**kwargs):
    """
    Getting network usage per service is included in the two steps.
    First of them is collecting usages per ip and the second one is matching
    ip with service

    :param datetime today: Date for which usages will be collects
    :returns tuple: Status, message and kwargs
    :rtype tuple:
    """
    try:
        default_service = Service.objects.get(
            ci_uid=settings.UNKNOWN_SERVICES['netflow'],
        )
    except Service.DoesNotExist:
        return False, 'Unknow service netflow does not exist'

    date = kwargs['today']
    new, updated, total = update(
        get_network_usages(date),
        get_usage_type(),
        default_service,
        date,
    )

    return True, '{0} new, {1} updated, {2} total'.format(
        new,
        updated,
        total,
    )
