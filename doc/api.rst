========
REST API
========

Scrooge provides simple REST API for pushing and pulling usages data
for your services. It consists of a single endpoint, and uses JSON as
a message format. After reading this guide you'll learn how to use it.


----------
Background
----------

Every pricing service [#]_ can upload data to Scrooge with the use of
its resources (e.g. requests count, transfer, etc.) by services. In
order to do that, there are some preconditions that must be satisfied:

* usage type(s) used by service must be added to Scrooge
* service has to be added to Scrooge (usually synchronized from Ralph)
* pricing service has to be added to Scrooge
* usage type(s) must be connected with the pricing service

A unique symbol has to be provided for every usage type in Scrooge,
which is later used to identify it in request processing.

The unit of resource usage doesn't matter (e.g. in the case of
transferring kB, MB, GB) - the most important thing is to keep the
unit of every usage the same (this rule applies to "abstract" units as
well) - after all, the cost of service is distributed to other
services proportionally to their usages (of resources).

If the pricing service has more than one usage type, it is necessary
to provide their percentage division in the period of time
(e.g. transfer - 30%, requests count - 70%, which means that 30% of
the total cost of pricing service is distributed proportionally to the
transfer usage and 70% proportionally to the requests count).


-------------
Prerequisites
-------------

In Scrooge's Admin:

  a. Create a new user, or use the account that is already provided for
     your service.

  b. Find what your API key is (under "User" -> "Preferences" -> "API
     Key").

  b. Create a Usage Type (one or more) that reflects resources used by
     your pricing service by visitng
     ``/admin/ralph_scrooge/usagetype/add/``. Remember that every
     service usage type must have a unique symbol.

    * Leave "Show usage type in report" checked.
    * Type: select "Service usage type".

  c. Create Pricing Service by visiting
     ``/admin/ralph_scrooge/pricingservice/add/``. Possible options
     for pricing service:

    * Plugin type – use ``universal``, if pricing service costs should
      be allocated proportionally to usage types (total real cost of
      pricing service will be divided into other services). Use
      ``fixed price`` if you'll provide price for every unit of usage
      type used by this pricing service (like AWS billing, where you
      are charged fixed price by every hour of working instance;
      notice that sum of this cost could be different than real
      pricing service cost).
    * Services – select services which total cost will be summed up to
      pricing service cost (usually it should be 1:1 mapping)
    * Service usage types – select usage type(s) created in the
      previous step. Notice that only usage types with the “Service
      usage type” are presented here. If you only have one usage type
      for your service, select it and type 100 in its percentage
      field.


-------------------
Pushing usages data
-------------------

Send your usages data to ``/scrooge/api/v0.9/pricingserviceusages/``
endpoint, using POST method. Your data should be in JSON format, with
the structure described below. Authorization is done with
``Authorization`` HTTP header containing your user name and API key
generated in Scrooge's Admin.


"""""""""""""""""""""""
Expected data structure
"""""""""""""""""""""""
.. _expected-data-structure:

::

  {
    "pricing_service": "<pricing service name or ID>",
    "date": "<date>",
    ["overwrite: "no | values_only | delete_all_previous"],
    "usages": [
        {
            "pricing_object": "<pricing_object_name>" |
            (
              ("service": "<service name>" | "service_id": <service ID> | "service_uid": "<service UID>"),
              "environment": "<environent name>",
            )
            "usages": [
                {
                    "symbol": "<usage type symbol>",
                    "value": <actual usage without units>
                },
                ...
            ]
        },
        ...
    ]
  }

As you can see, the ``overwrite`` field is optional - its default
value is ``no`` (see below for the description of all of its values).

Please note that you could provide here either service being charged
(given either by its name, ID or UID), which will be charged directly,
or the pricing object (e.g. hostname or IP address) - the service
assigned to this pricing object will be charged implicitly. In the
former case (i.e., providing service instead of pricing object), you
need to specify the name of the environment as well. You can mix all
those three forms in a single request, as shown in the example below,
but the preferred form is by specifying pricing object.

Example::

  POST http://localhost:8080/scrooge/api/v0.9/pricingserviceusages/
  Content-Type: application/json
  Authorization: ApiKey <user name>:<API key from Scrooge Admin>
  {
      "pricing_service": "pricing_service1",
      "date": "2016-09-02",
      "usages": [
          {
              "service": "service1",
              "environment": "env1",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 123
                  },
                  {
                      "symbol": "transfer",
                      "value": 321
                  }
              ]
          },
          {
              "pricing_object": "pricing_object1",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 543
                  },
                  {
                      "symbol": "transfer",
                      "value": 565
                  }
              ]
          },
          {
              "service_id": 123,
              "environment": "env2",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 788
                  },
                  {
                      "symbol": "transfer",
                      "value": 234
                  }
              ]
          },
          {
              "service_uid": "sc-123",
              "environment": "env2",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 788
                  },
                  {
                      "symbol": "transfer",
                      "value": 234
                  }
              ]
          }
      ]
  }


"""""""""""""""""""""""""""
Overwriting previous values
"""""""""""""""""""""""""""

The aforementioned ``overwrite`` field defines a way how to treat
previous service usage values uploaded for the same date and usage
type. There are three possible actions here:

* ``delete_all_previous`` - all previously upladed daily usages for
  the same date, with the same usage type should be deleted - only
  usages from the 2nd upload should remain, despite the fact that 1st
  upload contained daily usage for different service environment than
  the 2nd one. Example::

    1st upload (same day, same usage type):
    daily usage 1: service env 1, value 40
    daily usage 2: service env 2, value 60

    2nd upload (same day, same usage type):
    daily usage 1: service env 1, value 50

    final result:
    daily usage 1: service env 1, value 50

* ``values_only`` - all previously uploaded daily usages from the same
  date, with the same usage type *and the same service environment*
  should be replaced by the new daily usage - the ones with different
  service environment should remain untouched. Example::

    1st upload (same day, same usage type):
    daily usage 1: service env 1, value 40
    daily usage 2: service env 2, value 60

    2nd upload (same day, same usage type):
    daily usage 1: service env 1, value 50

    final result:
    daily usage 1: service env 2, value 60
    daily usage 2: service env 1, value 50

* ``no`` - nothing gets deleted/replaced, new daily usages should be
  added to the existing ones, despite the fact that it has the same
  service environment as the one from the previous upload. Example::

    1st upload (same day, same usage type):
    daily usage 1: service env 1, value 40
    daily usage 2: service env 2, value 60

    2nd upload (same day, same usage type):
    daily usage 1: service env 1, value 50

    final result:
    daily usage 1: service env 1, value 40
    daily usage 2: service env 2, value 60
    daily usage 3: service env 1, value 50

Please note that in case of uploading your data via pricing object
(instead of service and environment, see expected-data-structure_),
its service environment is implicitly given.

"""""""""""""""""""""""""""""""
Possible responses (HTTP codes)
"""""""""""""""""""""""""""""""

201 - everything OK, data is saved successfully.

400 - invalid symbol or name (e.g. usage type or service) - such error
will will contain an additional information about invalid data.

401 - authorization/authentication error.

405 - method not allowed (e.g. when you try to access pull endpoint
with POST or push endpoint with GET).

500 - error on server side during data processing, which should be
reported to us.


-------------------
Pulling usages data
-------------------

Usages that are already stored in Scrooge for a given pricing service
(identified by ``pricing_service_id``) and date, can be fetched by
sending a GET request to:
``/scrooge/api/v0.9/pricingserviceusages/<pricing_service_id>/<date(YYYY-MM-DD)>/``.

Example::

  GET http://localhost:8080/scrooge/api/v0.9/pricingserviceusages/111/2016-09-02/
  Authorization: ApiKey <user name>:<API key from Scrooge Admin>
  {
    "pricing_service": "pricing_service1",
    "pricing_service_id": 111,
    "date": "2016-09-02",
    "usages": [
      {
        "service": "service1",
        "service_id": 123,
        "environment": "env1",
        "pricing_object": "pricing_object1",
        "usages": [
          {
            "symbol": "requests",
            "value": 123
          },
          {
            "symbol": "transfer",
            "value": 321
          }
        ]
      }
      ...
    ]
  }


.. [#] Pricing Service is financial extension to regular service. It
       contains information about methods of service costs allocation,
       services excluded from charging etc.
