============
Installation
============
Scrooge contains ralph in its requirements, because it is a plugin for ralph. For more information on how to configure or install ralph, please refer to its documentation.

Install Scrooge
~~~~~~~~~~~~~~~
There are two ways to install Scrooge. One of them is a simple pip installation which is nice and easy. Installation from sources require Scrooge to be downloaded from github and then, installed manually

Install Scrooge from pip
------------------------
A fast and easy way is to install Scrooge from pip::

  (ralph)$ pip install scrooge

That's it.

Install Scrooge from sources
----------------------------
It is also possible to install Scrooge from sources. To do this, first, you need to download Scrooge from github::

  (ralph)$ git clone git://github.com/allegro/ralph_pricing.git

Enter to the project folder::

  (ralph)$ cd ralph_scrooge

and install it::

  (ralph)$ pip install -e .

The Scrooge requirements (ralph, ralph_assets) will be installed automatically


Upgrade existing installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To upgrade Scrooge, you need to stop any Ralph processes that are running. It is good practice not to upgrade the old version, but create a separate virtual environment and install everything from the begin, but if you need to upgrade the old version, be sure that everything is stopped.


Upgrade Scrooge from pip
------------------------
If you installed Scrooge from pip, then you can simply::

    (ralph)$ pip install --upgrade scrooge

After it is finished, upgrade the static files::

    (ralph)$ ralph collectstatic

Upgrade Scrooge from sources
----------------------------
First, you need to download Scrooge from github::

  (ralph)$ git clone git://github.com/allegro/ralph_pricing.git

Enter to the project folder::

  (ralph)$ cd ralph_scrooge

and upgrade it::

  (ralph)$ pip install --upgrade -e .

Finally, you need to upgrade the static files::

    (ralph)$ ralph collectstatic

Migrate the database
~~~~~~~~~~~~~~~~~~~~
Some of updates require database migrations. To migrate a database, you need to run::

    (ralph)$ ralph migrate ralph_scrooge

Be sure that you have a backup of your database. Sometimes you can migrate data or create some complicated and unwanted changes.

Update the settings
~~~~~~~~~~~~~~~~~~~~
Some new features added to Ralph may require additional settings to work properly. In order to enable them in your settings, follow the instructions in the :doc:`change log <changes>` for the version you have installed.

Testing if it works
~~~~~~~~~~~~~~~~~~~
To be sure that everything work fine, is recommended to run unit tests. To do this, run::

  (ralph)$ DJANGO_SETTINGS_PROFILE=test-pricing ralph test ralph_scrooge
