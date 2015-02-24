.. _customisation:

=============
Customisation
=============

Out of the box Atramhasis tries to make as few assumptions as possible about 
setup. We have taken care to ensure that significant parts of the application
are easy to customise and expect most installations to have custom code. We've 
shipped Atramhasis with sane defaults so you can get a quick feel for the
capabilities of the software. However, we do not advise running a production
instance with only these default settings.

.. _own_project:

Creating your own project
=========================

Whenever you want to run an instance of Atramhasis, you start by creating your
own project. This is the place where you will maintain and develop your own
custom templates, static assets such as stylesheets, your security implementation
and other general configuration. To make it easier on you to get started, we
provide a scaffold just for this. As always, we advise working in a 
virtual environment.

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
instances. First you need to tell python where to find such a provider by adding
this code just below the logging configuration:

.. code-block:: python

    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

Then you need to instantiate such a provider within the includeme function in
this file. This provider needs a few arguments: an id for the provider, an id
for the conceptscheme it's working with and a function that knows how the
provide a database session. The id for the provider is often a text string 
and will appear in certain url's and might popup in the user interface from 
time to time. The database sessionmaker can be found at 
`config.registry.dbmaker`. Finally, you need to register this provider with 
the :class:`skosprovider.registry.Registry`.

.. code-block:: python

    STUFF = SQLAlchemyProvider(                                                 
        {
            'id': 'STUFF',
            'conceptscheme_id': 1
        },                                 
        config.registry.dbmaker
    )

    skosregis.register_provider(STUFF)

After having registered your provider, the file should look more or less like 
this:

.. code-block:: python

    # -*- coding: utf-8 -*- 

    import logging
    log = logging.getLogger(__name__)
                 
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

                                                           
    def includeme(config):                                                 
        STUFF = SQLAlchemyProvider(
            {
                'id': 'STUFF',
                'conceptscheme_id': 1
            },
            config.registry.dbmaker
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
   vocabularies, please be sure to create the URI's before or during import 
   (possbily by using a relevant generator yourself).

Suppose you have decided that your URI's should look like this: 
`http://id.mydata.org/thesauri/stuff/[id]`. You can do this by registering
a :class:`~skosprovider.uri.UriPatternGenerator` with your provider:

.. code-block:: python

    STUFF = SQLAlchemyProvider(                                 
        {
            'id': 'STUFF',
            'conceptscheme_id': 1
        },
        config.registry.dbmaker,
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
            {
                'id': 'STUFF',
                'conceptscheme_id': 1
            },
            config.registry.dbmaker,
            uri_generator=UriPatternGenerator(
                'http://id.mydata.org/thesauri/stuff/%s'
            )
        )
        
        skosregis = config.get_skos_registry()                                      
        
        skosregis.register_provider(STUFF)

If you need more complicated URI's, you can easily write you own generator
with a small piece of python code. You just need to follow the interface
provided by :class:`skosprovider.uri.UriGenerator`.


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

One very easy technique to use, is :term:`Pyramid`'s 
:ref:`override assets mechanism <pyramid:overriding_assets_section>`. 
This allows you to override a core Atramhasis template with your own template.
Suppose we want to change the text on the Atramhasis homepage to welcome visitors 
to your instances. This text can be found in :file:`atramhasis/templates/welcome.jinja2`.

Assuming that you created your project as `my_thesaurus`, we can now create our
own template in :file:`my_thesaurus/templates/my_welcome.jinja2`. Please consult
the :term:`Jinja2` documentation if you need help with this.

Once you've created your template file, you just need to tell your project to
override the default :file:`welcome.jinja2` with your version. To do this you
need to configure the :term:`Pyramid` config object found in 
:file:`my_thesaurus.__init__.py`.

.. code-block:: python

    config.override_asset(                                                      
        to_override='atramhasis:templates/welcome.jinja2',                   
        override_with='templates/my_welcome.jinja2'                   
    )

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


Foreign Keys
============

Atramhasis will often function as a central part of a :term:`SOA` in an 
organisation. :class:`~skosprovider.skos.Concept` and maybe 
:class:`~skosprovider.skos.Collection` objects will be used by other applications. 
One of the riskier aspects of this is that someone might delete a concept in a 
certain scheme that is still being used by another application. Even worse, the 
user approving the delete might not even have a clue that the concept is being 
used by some external application. While in the decentralised world that is the
world wide web, we can never be sure that nobody is using our concept any more, 
we can take some steps to at least control what happens within other applications
that are within our control.

Of course, within the framework that is Atramhasis it's very difficult to know
how or where your own resources might be and how they might be using concepts
from Atramhasis. We have therefor provided the necessary hooks for you that can
help you deal with the sort of situation. But the actual implementation is left
up to you.

We have added a decorator :func:`~atramhasis.protected_resources.protected_operation`. 
When you add this decorator to a view, this view will emit a 
:class:`~atramhasis.protected_resources.ProtectedResourceEvent`. By default we
have added this decorator the :meth:`~atramhasis.views.AtramhasisCrud.delete_concept` 
view.

In you own code, you can subscribe to this 
:class:`~atramhasis.protected_resources.ProtectedResourceEvent` through the
usual :func:`pyramid.events.subscriber`. In this event handler you are then 
free to implement whatever check you need to do. If you find that the resource 
in question is being used somewhere and this operation
should thus not be allowed to proceed, you simply need to raise a 
:class:`atramhasis.protected_resources.ProtectedResourceException`. Into this
exception you can also pass a list of :term:`URI` that might provide the
user with some feedback as to where this concept might be used.

For example, a sample event handler that would make it impossible to delete
concepts with a URI of less than 5 characters:

.. code-block:: python

    from pyramid.events import subscriber
    from atramhasis.protected_resources import ProtectedResourceEvent

    @subscriber(ProtectedResourceEvent)
    def never_delete_a_short_uri(event):
        if len(event.uri) < 5:
            raise ProtectedResourceException(
                'resource {0} has a URI shorter than 5 characters, preventing this operation'.format(event.uri),
                []
            )


Adding Google Analytics
=======================

Out of the box, it's very easy to add Google Analytics integration to Atramhasis.
All you need to do is add you Web Property ID to :file:`development.ini`.

.. code-block:: ini

    # Enter your Google Analytics Web Property ID
    ga.tracker_key = UA-12345678-9

This will add basic analytics to every page, using a Jinja2 macro. If you need
more control over the code, you can override this macro in your own project. 
Suppose you always want to use SSL when sending data. First, you would create
you own macro, eg. in :file:`my_macros.jinja2` in the templates directory 
of your :ref:`own project <own_project>`.

.. code-block:: jinja

    {% macro ga_tracker(ga_key) %}
        <!-- Google Analytics -->
        <script type="text/javascript">
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ga('create', '{{ ga_key }}', 'auto');
        ga('set', 'forceSSL', true);
        ga('send', 'pageview');
        </script>
        <!-- End Google Analytics -->
    {% endmacro %}

Once that's done, you need to override the the ``ga`` block in the base template. To
do this, it's easiest to override Atramhasis' :file:`base.jinja2` in your own
project. To do that, add the following to your project's main function:

.. code-block:: python

    config.override_asset(                                                      
        to_override='atramhasis:templates/base.jinja2',                   
        override_with='templates/base.jinja2'                   
    )

In this file, you can now choose what should appear within the ga block defined
in :file:`staticbase.jinja2`. Here we are just replacing one macro with another,
but you are off course free to make further alterations.

.. code-block:: jinja

    {%- extends 'staticbase.jinja2' -%}

    {% block ga %}
        {% set ga_key = ga_key|default(request.registry.settings["ga.tracker_key"]) %}
        {% from 'my_macros.jinja2' import ga_tracker %}
        {% if ga_key %}
            {{ ga_tracker(ga_key) }}
        {% endif %}
    {% endblock %}

Adding external providers
=========================

Within your Atramhasis instance you can make use of external providers. These
are other systems serving up thesauri that you can interact with. Within the
admin interface you can create links to these thesauri as :term:`SKOS` matches.
This way you can state that a concept within your thesauri is the same as
or similar to a concept in the external thesaurus. And, more interestingly, 
you can also import concepts from such a thesaurus into your own vocabulary. 
Importing a concept like this will automatically create a :term:`SKOS` match 
for you. Once a match is in place, you can also update your local concept with
information from the external concept by performing a merge.

To enable all this power, you again need to configure a provider in you 
application. Continuing with our :ref:`example project <own_project>`, we need
to go back to our :file:`my_thesaurus/skos/__init__.py`. In this file you need
to register other instances of 
:class:`skosprovider.providers.VocabularyProvider`. Currently providers
have already been written for Getty Vocabularies, English Heritage vocabularies
and Flanders Heritage Vocabularies. Depending on the system you're trying to
interact with, writing a new provider is fairly simple. For this example, we'll
assume that you want to integrate the wealth of information that the 
`Art and Architecture Thesaurus (AAT)` vocabulary offers you.

The :class:`~skosprovider_getty.providers.AATProvider` for this 
(and other Getty vocabularies) is available as skosprovider_getty_ and is 
installed by default in an Atramhasis instance. All you need to do is configure 
it. First, we need to import the provider. Place this code at the top 
of :file:`my_thesaurus/skos/__init__.py`.

.. code-block:: python
    
    from skosprovider_getty.providers import AATProvider

Once this is done, we need to instantiate the provider within the `includeme`
function and register it with the :class:`skosprovider.registry.Registry`. This
is all quite similar to registering your own 
:class:`skosprovider_sqlalchemy.providers.SQLAlchemyProvider`. One thing you do
need to do, is tagging this provider with a subject. By adding the `external`
subject to the provider, we let Atramhasis know that this is not a regular, 
internal provider that can be stored in our database, but a special external
one that can only be used for making matches. As such, it will not be present
and visible to the public among your regular vocabularies.

.. code-block:: python

    AAT = AATProvider(
        {'id': 'AAT', 'subject': ['external']},
    )
    skosregis.register_provider(AAT)

That's all. You can do the same with the 
:class:`~skosprovider_getty.providers.TGNProvider` for the 
`Thesaurus of Geographic Names (TGN)` or any of the providers for 
`heritagedata.org <http://heritagedata.org>`_ that can be found in 
skosprovider_heritagedata_.

In the end your :file:`my_thesaurus/skos/__init__.py` should look somewhat like
this:

.. code-block:: python

    # -*- coding: utf-8 -*- 

    import logging
    log = logging.getLogger(__name__)
                 
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
    from skosprovider_getty.providers import AATProvider
    from skosprovider.uri import UriPatternGenerator

                                                           
    def includeme(config):                                                 
        STUFF = SQLAlchemyProvider(                                 
            {
                'id': 'STUFF',
                'conceptscheme_id': 1
            },
            config.registry.dbmaker,
            uri_generator=UriPatternGenerator(
                'http://id.mydata.org/thesauri/stuff/%s'
            )
        )

        AAT = AATProvider(
            {
                'id': 'AAT',
                'subject': ['external']
            }
        )
        
        skosregis = config.get_skos_registry()                                      
        
        skosregis.register_provider(STUFF)
        skosregis.register_provider(AAT)

Now you'll be able to import from the AAT to your heart's delight. For an 
extended example that adds even more providers, you could have a look at the
`demo` scaffold that comes with Atramhasis.

.. _skosprovider_getty: http://skosprovider-getty.readthedocs.org
.. _skosprovider_heritagedata: http://skosprovider-heritagedata.readthedocs.org
