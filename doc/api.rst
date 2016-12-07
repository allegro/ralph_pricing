========
REST API
========

Scrooge provides public REST API described by OpenAPI_-compliant
schema, which is available for consumption by external
programs/clients at ``/scrooge/api/schema.json``.

On top of this schema, we provide swagger-ui_ , which is available at
``/scrooge/api`` or ``/api`` endpoint (the latter just redirects to
the former). It serves both as documentation and convenience tool,
that is meant to facilitate human interaction with our API and improve
its discoverability.


.. _OpenAPI: https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md

.. _swagger-ui: https://github.com/swagger-api/swagger-ui
