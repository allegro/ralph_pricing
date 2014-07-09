.. image:: https://pypip.in/v/scrooge/badge.png
    :target: https://crate.io/packages/scrooge/
    :alt: Latest PyPI version


.. image:: https://pypip.in/d/scrooge/badge.svg
    :target: https://crate.io/packages/scrooge/
    :alt: Number of PyPI downloads


.. image:: https://travis-ci.org/allegro/ralph_pricing.svg?branch=develop
    :target: https://travis-ci.org/allegro/ralph_pricing


.. image:: https://coveralls.io/repos/allegro/ralph_pricing/badge.png?branch=develop
  :target: https://coveralls.io/r/allegro/ralph_pricing?branch=develop


.. image:: https://pypip.in/license/scrooge/badge.svg
    :target: https://crate.io/packages/scrooge/

The pricing module aggregates data from Ralph and from Ralph Assets to generate
reports showing the prices of the servers in inventory per their owners daily.

============
Installation
============
Scrooge contains ralph in requirements because is plugin for ralph. For more information how to configure or install ralph refer to ralph documentation.

Install Scrooge
~~~~~~~~~~~~~~~
There are two way to install scrooge, one of them is simple pip installation and it is easy and pleasant. Installation from sources require download scrooge from github and manually installation them.

Install Scrooge from pip
------------------------
Faster and easier way is install scrooge from pip::

  (ralph)$ pip install scrooge

That's it.

Install Scrooge from sources
----------------------------
Also, there is a possible to install scrooge from sources. If you wanna do that, you need to download scrooge from github before.::

  (ralph)$ git clone git://github.com/allegro/ralph_pricing.git

Enter to the project folder::

  (ralph)$ cd ralph_pricing

and install them::

  (ralph)$ pip install -e .

The scrooge requirements (ralph, ralph_assets) will be installed automatically.

Upgrade existing installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For upgrade scrooge you need stop any Ralph processes that is running. Good practice is not upgrading old version but create separated virtualenv and install there everything from the begin but if you need upgrade old version just be sure that everything is stopped.

Upgrade Scrooge from pip
------------------------
If you installed from pip, then you can simply do::

    (ralph)$ pip install --upgrade scrooge

When upgrade will be finished, upgrade the static files::

    (ralph)$ ralph collectstatic

Upgrade Scrooge from sources
----------------------------
You need to download scrooge from github before.::

  (ralph)$ git clone git://github.com/allegro/ralph_pricing.git

Enter to the project folder::

  (ralph)$ cd ralph_pricing

and upgrade them::

  (ralph)$ pip install --upgrade -e .

at the end you need to upgrade the static files::

    (ralph)$ ralph collectstatic

Migrate the database
~~~~~~~~~~~~~~~~~~~~
Some of updates require database migrations. For migrate database just run::

    (ralph)$ ralph migrate ralph_pricing

Be sure that you have backup of your database. Some of migrations could migrate any data or create some complicate changes and unwanted for you changes.

Update the settings
~~~~~~~~~~~~~~~~~~~~
Some new features added to Ralph may require additional settings to work
properly. In order to enable them in your settings, follow the instructions in
the :doc:`change log <changes>` for the version you installed.

Testing if it works
~~~~~~~~~~~~~~~~~~~
For be sure that everything work fine, is recommended to run unit tests. For do this just run::

  (ralph)$ DJANGO_SETTINGS_PROFILE=test-pricing ralph test ralph_pricing

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

OPENSTACK_EXTRA_QUERIES <list of tuple> - Extra queries for openstacp

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
