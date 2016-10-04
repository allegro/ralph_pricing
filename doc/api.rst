========
REST API
========

Scrooge provides public REST API that uses JSON as its message
format. This API is available at ``/scrooge/api/v0.9/`` and consists
of the following endpoints:

* ``api-token-auth`` - for obtaining auth tokens;
* ``pricingserviceusages`` - for uploading/fetching usages data;
* ``teamtimedivision`` - for uploading/fetching divisions of teams time.

After reading this guide you'll learn how to use them.

-------------
Authorization
-------------

Using Scrooge's API requires authorization. It is token-based, so each
of your requests has to contain ``Authorization`` header in one of the
following formats::

  Authorization: Token <your API key>

or::

  Authorization: ApiKey <your user name>:<your API key>

The former one is preferred, while the latter is only for backwards
compatibility, so don't rely on it for too long, as we may drop
support for it at some point.

If you don't know what your API key is, you can obtain it by sending a
POST request with your user's credentials to ``api-token-auth``
endpoint. Example::

  POST http://localhost:8000/scrooge/api/v0.9/api-token-auth/
  Content-Type: application/json
  {
      "username": "my_technical_user",
      "password": "my_technical_user_password"
  }

Response::

  {
    "token": "401f7ac837da42b97f613d789819ff93537bee6a"
  }


---------------------
Possible status codes
---------------------

Our API uses a subset of standard HTTP status code, i.e.:

* ``200/201`` - everything OK, data fetched/saved successfully.

* ``400`` - invalid or mis-shaped data - such error will will contain
  an additional description of what is wrong.

* ``401`` - authorization/authentication error.

* ``405`` - method not allowed (e.g. when you try to access pull
  endpoint with POST or push endpoint with GET).

* ``500`` - error on server side during data processing, which should
  be reported to us.

In case of ``4xx`` errors, the content of received response will
contain more detailed info about the reason behind the error.


-----------
Usages Data
-----------

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


++++++++++++++++
Uploading usages
++++++++++++++++

Before uploading your usages, you need to do two things:

  1. Create a Usage Type (one or more) that reflects resources used by
     your pricing service by visiting
     ``/admin/ralph_scrooge/usagetype/add/``. Remember that every
     service usage type must have a unique symbol.

    * leave "Show usage type in report" checked.
    * select "Service usage type".

  2. Create Pricing Service by visiting
     ``/admin/ralph_scrooge/pricingservice/add/``. Possible options
     for pricing service:

    * plugin type – use ``universal``, if pricing service costs should
      be allocated proportionally to usage types (total real cost of
      pricing service will be divided into other services). Use
      ``fixed price`` if you'll provide price for every unit of usage
      type used by this pricing service (like AWS billing, where you
      are charged fixed price by every hour of working instance;
      notice that sum of this cost could be different than real
      pricing service cost);
    * services – select services which total cost will be summed up to
      pricing service cost (usually it should be 1:1 mapping);
    * service usage types – select usage type(s) created in the
      previous step. Notice that only usage types with the “Service
      usage type” are presented here. If you only have one usage type
      for your service, select it and type 100 in its percentage
      field.

After that, you can proceed with your upload. The expected data
structure is as follows::

  {
    "pricing_service": "<pricing service name or ID>",
    "date": "<date>",
    ["overwrite: "no | values_only | delete_all_previous"],
    ["ignore_unknown_services": "true | false"],
    "usages": [
        {
            "pricing_object": "<pricing_object_name>" |
            (
              ("service": "<service name>" | "service_id": <service ID (in Scrooge)> | "service_uid": "<service UID>"),
              "environment": "<environment name>",
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

As you can see, ``overwrite`` and ``ignore_unknown_services`` fields are
optional - their default value are ``no`` and ``false`` respectively (see below
for the description of all of their values).

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
  Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
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

The aforementioned ``overwrite`` field defines a way how to treat
previous service usage values uploaded for the same date and usage
type. There are three possible actions here:

* ``delete_all_previous`` - all previously uploaded daily usages for
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
  (or pricing object - see remark at the bottom of this section)
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
(instead of service and environment, see expected data structure
above), its service environment is implicitly given.


"""""""""""""""""""""""""
Ignoring unknown services
"""""""""""""""""""""""""

You could use field ``ignore_unknown_services`` to handle the case, when
incoming data might be invalid, ex. some of provided service-environment does
not exist. By default (or when this field is set to ``false``) this will result
in ``400`` error (Bad request). When you set it to ``true``, all invalid rows
will be ignored and their values will not be saved to Scrooge.


+++++++++++++++
Fetching usages
+++++++++++++++

Usages that are already stored in Scrooge for a given pricing service
(identified by ``pricing_service_id``) and date, can be fetched by
sending a GET request to:
``/scrooge/api/v0.9/pricingserviceusages/<pricing_service_id>/<date(YYYY-MM-DD)>/``.

Example::

  GET http://localhost:8080/scrooge/api/v0.9/pricingserviceusages/111/2016-09-02/
  Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
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


--------------------
Teams Time Divisions
--------------------

Teams Time Divisions allow to allocate your team's working time (and
therefore costs) into some services (e.g., projects that your team has
been working on). The granularity of such allocations are
per-month.

+++++++++++++++++++
Uploading divisions
+++++++++++++++++++

Let's start with an example::

  POST http://127.0.0.1:8000/scrooge/api/v0.9/teamtimedivision/123/2016/9/
  Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
  Content-Type: application/json
  {
    "division": [
      {
        "service_uid": "uid-111",
        "environment": "prod",
        "percent": 70.0
      },
      {
        "service_uid": "uid-111",
        "environment": "test",
        "percent": 10.0
      },
      {
        "service_uid": "uid-333",
        "environment": "prod",
        "percent": 10.0
      },
      {
        "service_uid": "uid-444",
        "environment": "prod",
        "percent": 10.0
      }
    ]
  }

Here, we can see that our team (given in URL by its ID, i.e. ``156``)
did some work in March 2016 for four different services - most of this
work (and therefore time, and therefore costs) was spent on
``uid-111/prod`` (70%), and the rest of it was spent on three
remaining services (10% for each one of them). There are a couple of
important things to keep in mind here:

* services given as ``uid-111/prod`` and ``uid-111/test`` are two
  different entities, despite the fact that they both share the same
  UID;
* percents from the same division should sum up exactly to 100% - if
  you try to upload a division like 70+10+10 (or 70+10+10+20), you'll
  get a validation error.
* when you upload two or more divisions for the same team and date
  (year+month), only the last one of them is taken into account (i.e.,
  it effectively overwrites previous ones);
* all the fields are required, and your division requires at least one
  ``service_uid/environment/percent`` object to be present (in such
  case, its ``percent`` field should equals ``100.0``).

++++++++++++++++++
Fetching divisions
++++++++++++++++++

This operation is provided for symmetry to upload (in case you'd need
to check if Scrooge has correct divisions for your team - although you
can look at this data via Scrooge's GUI as well) and it has the same
form except that you don't send any content. Example::

  GET http://127.0.0.1:8000/scrooge/api/v0.9/teamtimedivision/123/2016/9/
  Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a

Response::

  {
    "division": [
      {
        "service_uid": "uid-111",
        "environment": "prod",
        "percent": 70.0
      },
      {
        "service_uid": "uid-111",
        "environment": "test",
        "percent": 10.0
      },
      {
        "service_uid": "uid-333",
        "environment": "prod",
        "percent": 10.0
      },
      {
        "service_uid": "uid-444",
        "environment": "prod",
        "percent": 10.0
      }
    ]
  }


.. note:: ``teamtimedivision`` endpoint is only accessible to team
   managers (both for read and write). A team manager in Scrooge's is
   a person who is associated with a team, and is an owner of at least
   one service, so this term has a little bit different meaning than
   in the real world. In practice however, it boils down to make these
   two aforementioned changes (i.e., make someone an owner and
   associate this person with given team) to any regular user in
   Scrooge Admin.


.. [#] Pricing Service is financial extension to regular service. It
       contains information about methods of service costs allocation,
       services excluded from charging etc.
