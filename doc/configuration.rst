=============
Configuration
=============

Configuration is available in file settings.py and there you should implement your settings.

PLUGGABLE_APPS <list of strings> - List with available applications for ralph

::

    PLUGGABLE_APPS += ['scrooge']

VIRTUAL_VENTURE_NAMES <list of strings> - venture names for virtual devices

::

    VIRTUAL_VENTURE_NAMES = ['venture1', 'venture2']

SCROOGE_SENTRY_DSN <string> - Full address with API key to sentry

::

    SCROOGE_SENTRY_DSN = 'http://xxxxxx:yyyyyy@sentry/zz'

CURRENCY <string> - This currency will be added to each value on report. It is prefix to cost value.

::

    CURRENCY = 'PLN'

HAMSTER_API_URL <string> - Url to hamster API

::

    HAMSTER_API_URL = 'http://xxxxxxx/'

RQ_QUEUE_LIST <tuple of strings> - List of queue names

::

    RQ_QUEUE_LIST += ('reports', 'reports_pricing')

SSH_NFSEN_CREDENTIALS <dict> - Credentials for servers

::

    SSH_NFSEN_CREDENTIALS = {
        'xxx.xxx.xxx.xxx': {
            'login': 'xxx',
            'password': 'xxx',
        },
        'yyy.yyy.yyy.yyy': {
            'login': 'yyy',
            'password': 'yyy',
        },
    }

NFSEN_CHANNELS <list of strings> - Channels like IN or OUT

::

    NFSEN_CHANNELS = ['xxx-OUT', 'xxx-IN', 'yyy-OUT', 'yyy-IN']

NFSEN_FILES_PATH <string> - Path to nfsen data files on remote server

::

    NFSEN_FILES_PATH = 'xxx/yyy/zzz'

NFSEN_CLASS_ADDRESS <list of strings> - Available class addresses

::

    NFSEN_CLASS_ADDRESS = [
        'xxx.xxx.xxx.x/yy'
        'zzz.zzz.zzz.z/yy'
    ]

OPENSTACK_USER <string> - User login name to openstack

::

    OPENSTACK_USER = 'xxx'

OPENSTACK_PASSWORD <string> - User password for given user name

::

    OPENSTACK_PASSWORD = 'yyy'

OPENSTACK_URL <string> - Url to openstack

::

    OPENSTACK_URL = 'yyy'

OPENSTACK_REGIONS <list of strings> - Datacenter names

::

    OPENSTACK_REGIONS = ['xxx', 'yyy']

OPENSTACK_EXTRA_QUERIES <list of tuple> - Extra queries for openstack

::

    OPENSTACK_EXTRA_QUERIES = [('http://xxx', 'yyy'), ('http://zzz', 'aaa')]

SCALEME_API_URL <string> - Url to scaleme

::

    SCALEME_API_URL = 'http://xxxxxxx/'

SPLUNK_HOST <string> - Splunk host name

::

    SPLUNK_HOST = 'http://xxxxxxx/'

SPLUNK_USER <string> - Splunk user name

::

    SPLUNK_USER = 'xxx'

SPLUNK_PASSWORD <string> - Password for splunk user

::

    SPLUNK_PASSWORD = 'yyy'
