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

.. _own_project:

Creating your own project
=========================

To hold you custom templates, security module and configuration, you can use
a scaffold we have provided. As always, we advise working in a virtual environment.

.. code-block:: bash    
    
    $ mkvirtualenv my_thesaurus
    $ pip install atramhasis
    $ pcreate -s atramhasis_scaffold my_thesaurus
    # Install dependencies
    $ pip install -r requirements-dev.txt
    # compile the Message Catalog Files
    $ python setup.py compile_catalog

This gives you a clean slate to start your customisations on. By default the
scaffold comes with a simple SQLite database. This is more than enough for
your first experiments and can even be used in production environment if your
needs are modest. You can always instruct Atramhasis to use 
some other database engine, as long as SQLAlchemy supports it. Configure the
`sqlalchemy.url` configuration option in :file:`development.ini` to change
the database. See the documentation of SQLAlchemy for more information about 
this connection url. After settings this url, run :command:`alembic` to
initialise and migrate the database to the latest version.

.. code-block:: bash

    # Create or update database based on 
    # the configuration in development.ini
    $ alembic upgrade head

Your custom version of Atramhasis can now be run. Run the following command
and point your browser to `http://localhost:6543` to see the result.

.. code-block:: bash

    $ pserve development.ini

Of course, this does not do very much since your Atramhasis is now running,
but does not contain any ConceptSchemes. You will need to configure this by 
entering a database record for the ConceptScheme and writing a small piece
of code.

To enter the database record, you need to enter a record in the table 
`conceptscheme`. In this table you need to register an id for the conceptscheme
and a uri. The id is for internal database use and has no other meaning. The
uri can be used externally. To register a new ConceptScheme in the sqlite 
database that was created:

.. code-block:: bash

    $ sqlite3 my_thesaurus.sqlite

.. code-block:: sql

    INSERT INTO conceptscheme VALUES (1, 'urn:x-my-thesaurus:stuff')

This take care of the first step. Now you also need to tell Atramhasis where
to find your conceptscheme and how to handle it. To do this, you need to edit
the file called :file:`my_thesaurus/skos/__init__.py`. In this file you need
to register :class:`~skosprovider_sqlalchemy.providers.SQLAlchemyProvider`
instances. First you need to tell python where to such a provider by adding
this code just below the logging configuration:

.. code-block:: python

    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

Then you need to instantiate such a provider within the includeme function in
this file. This provider needs a few arguments: an id for the provider, an id
for the conceptscheme it's working with and a database session. The id for
the provider is often a text string and will appear in certain url's and 
might popup in the user interface from time to time. The database session
can be claimed by calling `config.registry.dbmaker()`. Finally, you need to
register this provider with the :class:`skosprovider.registry.Registry`.

.. code-block:: python

    STUFF = SQLAlchemyProvider(                                                 
        {'id': 'STUFF', 'conceptscheme_id': 1},                                 
        config.registry.dbmaker()                                               
    )

    skosregis.register_provider(STUFF)

After having registered your provider, the file should loke more or less like 
this:

.. code-block:: python

    # -*- coding: utf-8 -*- 

    import logging
    log = logging.getLogger(__name__)
                 
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

                                                           
    def includeme(config):                                                 
        STUFF = SQLAlchemyProvider(                                 
            {'id': 'STUFF', 'conceptscheme_id': 1},
            config.registry.dbmaker()
        )
        
        skosregis = config.get_skos_registry()                                      
        
        skosregis.register_provider(STUFF)

Now you can restart your server and then you front page will show you a new,
but empty thesaurus. You can now start creating concepts and collections by
going to the admin interface at `http://localhost:6543/admin`.

You will notice that any concepts or collections you create wil get a 
:term:`URI` similar to `urn:x-skosprovider:STUFF:1`. This is due to the fact
that your :class:`~skosprovider_sqlalchemy.providers.SQLAlchemyProvider`
has a :class:`~skosprovider.uri.UriGenerator` that generates uris for the
provider. By default, the provider configures a 
:class:`~skosprovider.uri.DefaultUrnGenerator`, but it's expected that you
will want to override this.

.. warning::

   The :class:`~skosprovider.uri.UriGenerator` that you configure only generates
   URI's when creating new concepts or collections. When importing existing
   vocabularies, please be sure to create the URI's during importing (possbily
   by using a relevant generator yourself).

Suppose you have decided that your URI's should look like this: 
`http://id.mydata.org/thesauri/stuff/[id]`. You can do this by registering
a :class:`~skosprovider.uri.UriPatternGenerator` with your provider:

.. code-block:: python

    STUFF = SQLAlchemyProvider(                                 
        {'id': 'STUFF', 'conceptscheme_id': 1},
        config.registry.dbmaker(),
        uri_generator=UriPatternGenerator(
            'http://id.mydata.org/thesauri/stuff/%s'
        )
    )

Don't forget to import the :class:`~skosprovider.uri.UriPatternGenerator` at the
top of your file:

.. code-block:: python

    from skosprovider.uri import UriPatternGenerator

Your final file should look similar to this:

.. code-block:: python

    # -*- coding: utf-8 -*- 

    import logging
    log = logging.getLogger(__name__)
                 
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
    from skosprovider.uri import UriPatternGenerator

                                                           
    def includeme(config):                                                 
        STUFF = SQLAlchemyProvider(                                 
            {'id': 'STUFF', 'conceptscheme_id': 1},
            config.registry.dbmaker(),
            uri_generator=UriPatternGenerator(
                'http://id.mydata.org/thesauri/stuff/%s'
            )
        )
        
        skosregis = config.get_skos_registry()                                      
        
        skosregis.register_provider(STUFF)

If you need more complicated URI's, you can easily write you own generator
with a small piece of python code. You just need to follow the interface
provided by :class:`skosprovider.uri.UriGenerator`.
