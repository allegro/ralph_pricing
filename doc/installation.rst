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
