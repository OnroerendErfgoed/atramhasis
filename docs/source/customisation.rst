.. _customisation:

=============
Customisation
=============

Out of the box Atramhasis tries to make as few assumptions as possible about 
setup. We have taken care to ensure that significant parts of the application
are easy to customise and expect most installations to have custom code. Out of
the box Atramhasis comes with sane defaults so you can get a quick feel for the
capabilities of the software. However, we do not advise running a production
instance with only these default settings.

.. _appearance:

Appearance
==========

By implementing a few simple techniques from the :term:`Pyramid` web framework,
it's very easy to customise the look and feel of the public user interface. The
default implementation is a very neutral implementation based on the basic
elements in the Foundation framework. Customising and overriding this style is 
possible if you have a bit of knowledge about :term:`HTML` and :term:`CSS`.

You can also override the :term:`HTML` templates that Atramhasis uses without
needing to alter the originals so that future updates to the system will not
override your modifications.


.. _security:

Security
========

We assume that every deployment of Atramhasis has different needs when it comes
to security. Some instances will run on a simple laptop for testing and 
evaluation purposes, others might need a simple standalone database of users 
and certain deployments might need to integrate with enterprise authentication
systems like LDAP, Active Directory, Single Sign On, ...

Atramhasis provides authorisation hooks for security. To edit, add or delete a concept or collection,
a user is required to have the 'editor' pemission. Unless no authorisation policy has been configured.


Sample configuration
--------------------

The atramhasis_demo scaffold contains a sample security configuration, using Mozilla Persona:
http://www.mozilla.org/en-US/persona/. Persona security is implemented with pyramid_persona:
https://pypi.python.org/pypi/pyramid_persona

You can configure persona.secret and persona.audience in development.ini:

.. code-block:: python

    persona.secret = sosecret
    persona.audiences = http://localhost:6543

The login and logout views, the groupfinder and rootfactory are implemented in the security.py file.
