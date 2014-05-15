.. _security:

========
Security
========

Atramhasis provides authorisation hooks for security. To edit, add or delete a concept or collection,
a user is required to have the 'editor' pemission. Unless no authorisation policy has been configured.


Sample configuration
====================

The atramhasis_demo scaffold contains a sample security configuration, using Mozilla Persona.

In your projects __init__.py add some code to setup security. Add login and logout routes,
to handle login and logout requests from the client. Add an authentication policy and an authorization policy.
We used a root factory to define an ACL list for the objects.

.. code-block:: python

    # Set up security
    config.add_route('login', '/auth/login', request_method="POST")
    config.add_route('logout', '/auth/logout', request_method="POST")
    config.set_authentication_policy(AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(Root)


The login and logout views, the groupfinder and rootfactory are implemented in the security.py file.