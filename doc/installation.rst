Installation
===========

1. Install Ralph.

2. Install the ``ralph_pricing`` package from PyPi by running::
  
    pip install ralph_pricing


3. After installation add a line to the end of ``INSTALLED_APPS``::


    INSTALLED_APPS += (
    ...
    'ralph_pricing',
    )

4. Run::

    ralph migrate

5. Add a command that retrieves resource data from all the configured services to cron to be run daily::

    ralph pricing_sync

That's it. Now just run Ralph as described in its documentation, and login to
the Ralph system.  You will see an additional item, "Pricing" in the main menu.

