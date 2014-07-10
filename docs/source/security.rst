.. _security:

========
Security
========

Atramhasis provides authorisation hooks for security. To edit, add or delete a concept or collection,
a user is required to have the 'editor' pemission. Unless no authorisation policy has been configured.


Sample configuration
====================

The atramhasis_demo scaffold contains a sample security configuration, using Mozilla Persona:
http://www.mozilla.org/en-US/persona/. Persona security is implemented with pyramid_persona:
https://pypi.python.org/pypi/pyramid_persona

You can configure persona.secret and persona.audience in development.ini:

.. code-block:: python

    persona.secret = sosecret
    persona.audiences = http://localhost:6543

The login and logout views, the groupfinder and rootfactory are implemented in the security.py file.