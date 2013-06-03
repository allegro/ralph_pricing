Installation
===========

1. Install Ralph.

1. Install the ``ralph_pricing`` package from PyPi by running::
  
    pip install ralph_pricing


2. After installation add a line to the end of ``INSTALLED_APPS``::


    INSTALLED_APPS += (
    ...
    'ralph_pricing',
    )

3. Run::

    ralph migrate


That's it. Now just run Ralph as described in its documentation, and login to
the Ralph system.  You will see an additional item, "Assets" in the main menu.

