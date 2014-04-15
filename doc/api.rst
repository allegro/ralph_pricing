===
API
===
For improve usage and communication with scrooge we prepared api. Currently, there is only push api implemented and use to pushing usages data by services. In the future we plan create pull api for getting report data for single venture/service. For communication with API we use JSON as a message formant and REST API for maintenance of communication standards.

Push API
~~~~~~~~
Every service is obligate to pushing usages data to scrooge. Before you start using push api, first you need to create service and usages manually. When you have created service and usages then you can start push to scrooge by using api. http://ralph.office/scrooge/api/v0.9/serviceusages/ this is address for pushing data where current api version is 'v0.9'. Scrooge prefer collect data every day but if someone forgot do this then usages can be push for different dates.

**JSON FORMAT**

::

    {
        "service": "<service_symbol>",
        "date": "<date>",
        "venture_usages": [
            {
                "venture": "<venture_symbol>",
                "usages": [
                    {
                        "symbol": "<usage_type_1_symbol>",
                        "value": <usage1>
                    },
                  ...
                ]
            },
              ...
        ]
    }

**JSON EXAMPLE**

::

    {
        "service": "service_symbol",
        "date": "2111-11-11",
        "venture_usages": [
            {
                "venture": "venture1",
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
                "venture": "venture2",
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
                "venture": "venture3",
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

Pull API
~~~~~~~~

Coming soon...
