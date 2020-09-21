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
    $ cd my_thesaurus
    # Install dependencies
    $ pip install -r requirements-dev.txt
    # Download and install client side libraries
    $ cd my_thesaurus/static
    $ bower install
    $ cd admin
    $ bower install

This gives you a clean slate to start your customisations on.

Database
--------

By default the scaffold comes with a simple SQLite database. This is more than
enough for your first experiments and can even be used in production environment
if your needs are modest. You can always instruct Atramhasis to use
some other database engine, as long as SQLAlchemy supports it. Configure the
`sqlalchemy.url` configuration option in :file:`development.ini` to change
the database. See the documentation of SQLAlchemy for more information about
this connection url.

Database initialisation
.......................

To initialise the database, simply run the following.

.. code-block:: bash

    # Create or update database based on
    # the configuration in development.ini
    $ alembic upgrade head

.. _custom-alembic:

Custom alembic revisions
........................

If you have a need to create your own tables, or do custom database changes
we suggest you do so in another alembic branch next to the atramhasis branch.

First edit the :file:`alembic.ini` file so it contains the following:

.. code-block:: ini

    script_location = alembic
    version_locations = %(here)s/alembic/versions atramhasis:alembic/versions

Second, initialise alembic in your project:

.. code-block:: bash

    # alembic init alembic

This will create an alembic folder for your own revisions.

To create your first revision, the command is a little longer:

.. code-block:: bash

    $ alembic revision -m "first revision" --head=base --branch-label=myproject \
    --version-path=alembic/versions

.. note::

    if you need your alembic revisions to run after the atramhasis - for example
    if you want to create foreign keys to atramhasis tables - you can use
    :code:`--depends-on <hash>` where the hash is the latest revision hash from
    atramhasis. This hash can be found by using :code:`alembic heads`. In this
    example it is 184f1bbcb916

    .. code-block:: bash

        $ alembic heads
        184f1bbcb916 (atramhasis) (head)

Having created a revision like above will have created a second alembic branch.
Your alembic should have 2 heads now:

.. code-block:: bash

    $ alembic heads
    184f1bbcb916 (atramhasis) (effective head)
    975228f4f18c (myproject) (head)

Adding additional revisions will look like:

.. code-block:: bash

    alembic revision -m "second revision" --head=myproject@head

.. warning::

    Not using a seperate branch will add revisions to the atramhasis alembic
    branch. While this may work initially, this may create split branches
    and multiple heads when upgrading atramhasis in the future.

All generated revisions will `depends_on` the latest atramhasis revision at the
time of creating the scaffold to ensure atramhasis will run before your own
alembic. This is configured in the :file:`alembic/script.py.mako` file.

Whenever you would use `alembic upgrade head` to upgrade your database, you now
have to use **heads** plural instead.

.. code-block:: bash

    # Create or update database based on
    # the configuration in development.ini
    $ alembic upgrade heads


Running a local server
----------------------

Your custom version of Atramhasis can now be run. Run the following command
and point your browser to `http://localhost:6543` to see the result.

.. code-block:: bash

    $ pserve development.ini


Creating conceptschemes
-----------------------

Atramhasis is now running but does not contain any ConceptSchemes. You will
need to configure this by entering a database record for the ConceptScheme and
writing a small piece of code.

.. warning::

    Instantiating providers has changed between version 0.6.x and 0.7.0. Make
    sure to update your skos initialisation when updating. The old code is no
    longer supported, although the changes you need to make are minor.

To enter the database record, you need to enter a record in the table
`conceptscheme`. In this table you need to register an id for the conceptscheme
and a uri. The id is for internal database use and has no other meaning. The
uri can be used externally. To register a new ConceptScheme in the sqlite
database that was created:

.. code-block:: bash

    $ sqlite3 my_thesaurus.sqlite

.. code-block:: sql

    INSERT INTO conceptscheme VALUES (1, 'urn:x-my-thesaurus:stuff')

This takes care of the first step. Now you also need to tell Atramhasis where
to find your conceptscheme and how to handle it. To do this, you need to edit
the file called :file:`my_thesaurus/skos/__init__.py`. This is the default
location for creating a registry factory. Be default, this function is called
`create_registry`, but this can be changed in your development.ini file. The
function itself needs to receive the current request as a parameter and return
the instantiated :class:`skosprovider.registry.Registry`.

In this funcion you will register 
:class:`~skosprovider_sqlalchemy.providers.SQLAlchemyProvider`
instances to the SKOS registry. If not yet present, you need to tell Python where 
to find such a provider by adding this code to the top of the file:

.. code-block:: python

    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

Then you need to instantiate such a provider within the `create_registry` function in
this file. This provider needs a few arguments: an id for the provider, an id
for the conceptscheme it's working with and a connectionb to a database session.
The id for the provider is often a text string and will appear in certain url's 
and might popup in the user interface from time to time. The database session
is added to the Pyramid request that is passed to function and can be reached
as `request.db`. Finally, you need to register this provider with the 
:class:`skosprovider.registry.Registry`.

.. code-block:: python

    STUFF = SQLAlchemyProvider(
        {
            'id': 'STUFF',
            'conceptscheme_id': 1
        },
        request.db
    )

    registry.register_provider(STUFF)

After having registered your provider, the file should look more or less like
this:

.. code-block:: python

    # -*- coding: utf-8 -*-

    from skosprovider.registry import Registry
    from skosprovider.uri import UriPatternGenerator
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

    import logging
    log = logging.getLogger(__name__)


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        # create your own providers
        STUFF = SQLAlchemyProvider(
            {'id': 'STUFF', 'conceptscheme_id': 1},
            request.db
        )
    
        # Add your custom provider to the registry
        registry.register_provider(STUFF)

        # return the SKOS registry
        return registry


Now you can restart your server and then you front page will show you a new,
but empty thesaurus.

Creating concepts and collections
---------------------------------

You can now start creating concepts and collections by
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
        request.db,
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

    from skosprovider.registry import Registry
    from skosprovider.uri import UriPatternGenerator
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

    import logging
    log = logging.getLogger(__name__)


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        # create your own providers
        STUFF = SQLAlchemyProvider(
            {'id': 'STUFF', 'conceptscheme_id': 1},
            request.db,
            uri_generator=UriPatternGenerator(
                'http://id.mydata.org/thesauri/stuff/%s'
            )
        )
    
        # Add your custom provider to the registry
        registry.register_provider(STUFF)

        # return the SKOS registry
        return registry


If you need more complicated URI's, you can easily write you own generator
with a small piece of python code. You just need to follow the interface
provided by :class:`skosprovider.uri.UriGenerator`.

Hiding a vocabulary
===================

Atramhasis allows you to hide a vocabulary. This means the vocabulary is still
there as far as services are concerned and you can still edit it. But it will
not be visible in the public html user interface. You might want to use it for
small and rather technical vocabularies you need but don't want to draw
attention to. The only thing you need to do,
is tagging this provider with a subject. By adding the `hidden`
subject to the provider, we let Atramhasis know that this vocabulary should not 
be present among your regular vocabularies.

Suppose we wanted to hide our stuff:

.. code-block:: python

    # -*- coding: utf-8 -*-

    import logging
    log = logging.getLogger(__name__)

    from skosprovider.registry import Registry
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
    from skosprovider.uri import UriPatternGenerator


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        # create your own providers
        #
        STUFF = SQLAlchemyProvider(
            {
                'id': 'STUFF',
                'conceptscheme_id': 1,
                'subject': ['hidden']
            },
            request.db,
            uri_generator=UriPatternGenerator(
                'http://id.mydata.org/thesauri/stuff/%s'
            )
        )
    
        # Add your custom provider to the registry
        registry.register_provider(STUFF)

        # return the SKOS registry
        return registry


Now the STUFF thesaurus will not show up in the public web interface, but REST
calls to this conceptscheme will function as normal and you will be able to
maintain it from the admin interface.


.. _force_display_label_language:

Force a display language for a vocabulary
=========================================

Under normal circumstances, Atramhasis tries to provide the most
appropriate label for a certain concept or collection, based on some default
configuration and the preferences of the end-user. Every provider can be marked
as having a certain `default language` (English if not set), but Atramhasis
also tries to read what the user wants. It does this through the user's
browser's locale. This information can be read from the browser's HTTP headers
or cookies. Generally, Atramhasis just knows in what language a user is
browsing the site and tries to return labels appropriate for that language. So,
the same thesaurus visited from the US will return English labels, while it
will return Dutch when visited from Gent (Belgium).

You might have a vocabulary with a strongly preferential relation to a certain
language. We ran into this situation with a vocabulary of species: names for
plants and trees commonly found in Flanders. Some of them have one or more
local, Dutch, names. Most or all of them have an official name in Latin. The
normal language handling mechanism created a weird situation. It led to a tree
of names that was mostly in Latin, with the odd Dutch word thrown in for good
measure. This was not as desired by our users. To that end, a special mechanism
was created to force rendering labels of concepts and collections in a certain
language, no matter what the end-user's browser is requesting.

To set this, please edit the :file:`my_thesaurus/skos/__init__.py`. Look for the 
thesaurus you want to override and add a setting `atramhasis.force_display_label_language`
to the provider's metadata. Set it to a language supported by the provider
(there's little sense to setting it to a language that isn't present in the
vocabulary). Now Atramhasis will try serving concepts from this provider with
this language. All labels will still be shown, but the page title or current
label will be set to the selected language as much as possible. The normal
language determination mechanisms will keep on working, so if the concept has
no label in the requested language, Atramhasis will fall back on other labels
present.

Your provider should end up similar to this:

.. code-block:: python

    STUFF = SQLAlchemyProvider(
        {
            'id': 'STUFF',
            'conceptscheme_id': 1,
            'atramhasis.force_display_label_language': 'la'
        },
        request.db,
        uri_generator=UriPatternGenerator(
            'http://id.mydata.org/thesauri/stuff/%s'
        )
    )

Beware that this will only affect the Atramhasis UI, not the Atramhasis REST
services. We looked into some solutions for our problem that would have also
changed the underlying service, but decided against that because it would have
prevented you from making your own choices when interacting with Atramhasis. If
you want to render the tree of concepts using a preferred language different
from what a browser would advocate for, you can pass the language parameter in
a url, eg. `http://my.thesaurus.org/conceptschemes/STUFF/tree?language=la`.

.. _i18n:

Internationalisation
====================

When you create a new empty project with the `atramhasis` scaffold, you get an
English only version. The standard version of Atramhasis has been
translated in Dutch and French. If you desire, you can activate these by editing
your project's :file:`development.ini`

.. code-block:: ini

    # Edit and uncomment to activate nl and fr language support or other languages
    # you have added yourself.
    available_languages = en nl fr

Available languages should be a space separated list of IANA language codes. If
you add new languages, please consider contributing them back to the project.


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

Overriding templates
--------------------

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

.. note::

    Normally, to see the effect of the changes you made, you would need to
    restart your webserver. When developing, you can make use of the
    :command:`pserve` command's auto-reload feature. To do this, start your
    server like this:

    .. code-block:: bash

        $ pserve --reload development.ini

Changing the focal conceptschemes
---------------------------------

An Atramhasis instance should contain one or more conceptschemes. Four of your
conceptschemes can be picked to receive a little more attention and focus than
the other ones. These conceptschemes will appear on the homepagina with a list
of recently visited concepts in those schemes.

Selecting which conceptschemes receive this focus is done in your
:file:`development.ini` file.

.. code-block:: ini

    layout.focus_conceptschemes = 
      STUFF

This should be a space or newline delimited list, limited to 4 entries.

Changing the CSS
----------------

Out of the box, Atramhasis, comes with the Zurb Foundation framework. We have
created a custom style for this framework, but as always you are free to modify
this style. Your custom instance contains a few extension points that make it
easy to override and change style elements without having to rewrite to much
css. All style related files can be found in the :file:`my_thesaurus/static`
folder. This project's CSS is being maintained and generated by `Compass`. You
will find a :file:`scss` folder that contains three files that can be used for
easy customisations: :file:`_my_thesaurus-settings.scss`, 
:file:`_my_thesaurus.scss` and :file:`_my_thesaurus-admin.scss`. The first file
is a settings file that allows you to override a lot of variables that are used
in generating the css. Suppose you want to override the default row width and
the default font. You would change :file:`_my_thesarus-settings.scss` to the
following:

.. code-block:: scss

    // Custom SASS code for my_thesaurus

    $row-width: rem-calc(1140);
    $body-font-family: "museo-sans", "Open Sans", "Helvetica", Helvetica, Arial, sans-serif;

To have you changes take effect, you need to recompile the scss files and
restart your webserver.

.. code-block:: bash

    $ compass compile
        write css/app-admin.css
        write css/app.css

The other two files, :file:`_my_thesaurus.scss` and
:file:`_my_thesaurus-admin.scss` are the final scss files loaded before
compiling them and can be used to overwrite things in the public or admin
interface.


.. _security:

Security
========

We assume that every deployment of Atramhasis has different needs when it comes
to security. Some instances will run on a simple laptop for testing and
evaluation purposes, others might need a simple standalone database of users
and certain deployments might need to integrate with enterprise authentication
systems like LDAP, Active Directory, Single Sign On, ...

Atramhasis provides authorisation hooks for security. To edit, add or delete a 
concept or collection, a user is required to have the 'editor' pemission. Unless 
no authorisation policy has been configured.

To get started, consult the sections of the Pyramid documentation on security.

Prior to version 0.6.3, Atramhasis contained a demo scaffold that had a custom
security implementation using Mozilla Persona. Since this service has been
discontinued, the security configuration was removed as well. But you can still
check out the old code in our Github repository to see how it works.


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
    registry.register_provider(AAT)

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

    from skosprovider.registry import Registry
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
    from skosprovider_getty.providers import AATProvider
    from skosprovider.uri import UriPatternGenerator


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        STUFF = SQLAlchemyProvider(
            {
                'id': 'STUFF',
                'conceptscheme_id': 1
            },
            request.db,
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

        registry.register_provider(STUFF)
        registry.register_provider(AAT)

        return registry


Now you'll be able to import from the AAT to your heart's delight. For an
extended example that adds even more providers, you could have a look at the
`demo` scaffold that comes with Atramhasis.

.. _skosprovider_getty: http://skosprovider-getty.readthedocs.org
.. _skosprovider_heritagedata: http://skosprovider-heritagedata.readthedocs.org

Import a controlled vocabulary
==============================

Atramhasis includes a script :file:`atramhasis/scripts/import_file.py` which
helps you import an existing vocabulary from a file. It supports a few
different file types, but not every file type supports the full Atramhasis
datamodel.

The supported file types:

- RDF using :class:`~skosprovider_rdf.providers.RDFProvider`. This provider supports
  the full datamodel. Since the heavy lifting is done by `RDFlib`, most of the
  dialects supported by `RDFlib` should work. The full list can be found in
  `rdflib.util.SUFFIX_FORMAT_MAP`. Formats like `rdf/xml` and `turtle` should
  work.
- CSV (.csv) using :class:`~skosprovider.providers.SimpleCsvProvider`.
  The provider only supports importing and id, a prefLabel, a note and a source.
  It will work well when importing a simple flat list, but not for complex
  hierarchies.
- JSON (.json) using :class:`~skosprovider.providers.DictionaryProvider`. This
  provider supports the full datamodel.

Some things to take into account:

- Atramhasis only supports concepts with a numeric id. This ensures they can be
  auto-generated when adding new concepts or collections. These map to the
  `concept_id` attribute in the database, which is unique per conceptscheme as
  opposed to the `id` attribute that is unique for the entire database.
- When importing from an RDF vocabulary, the id will be read from a `dc` or
  `dcterms` `identifier` property if present. Please ensure this property 
  contains a numeric id, not a string or a URI.
- When importing from RDF, the import file could possibly contain more than one
  conceptscheme. Please ensure only one conceptscheme is present or
  no conceptschemes are presents and specify the URI and label on the command
  line.
- When importing from CSV or JSON, the data file only contains the concepts and
  collections in the scheme, but not the conceptscheme itself. In this case,
  please specify the URI and label of the conceptscheme on the command line.

The script can be called through the commandline in the project virtual environment.
Call it with the `help` argument to see the possible arguments.

.. code-block:: bash

    $ workon my_thesarus
    $ import_file --help

    usage: import_file [--from path_input_file] [--to conn_string] [--conceptscheme_label cs_label]
     (example: "import_file --from atramhasis/scripts/my_file --to sqlite:///atramhasis.sqlite --conceptscheme_label Labels")

    Import file to a database

    optional arguments:
      -h, --help            show this help message and exit
      --from INPUT_FILE     local path to the input file
      --to TO               Connection string of the output database
      --conceptscheme_label CS_LABEL
                            Label of the conceptscheme


The `from` argument is required and details where the file you want to import is
located, for example :file:`my_thesaurus/data/trees.json`. It is relative to your
current location.

The `to` argument contains the connection string of output database. Only
PostGreSQL and SQLite are supported. The structure is either
`postgresql://username:password@host:port/db_name` or
either `sqlite:///path/db_name.sqlite`. The default value is `sqlite:///atramhasis.sqlite`.

The data is loaded in a :class:`~skosprovider_sqlalchemy.models.ConceptScheme`. With a 
:class:`~skosprovider_rdf.providers.RDFProvider` the conceptscheme can be present
in the RDF file. The other providers can specify it on the command line
through the `conceptscheme_label` argument. If no `conceptscheme_label` is present,
the default label is the name of the file.

Once the data is loaded in the database, the configuration of the added provider must be
included in the :file:`my_thesaurus/skos/__init__.py`. A successfull run of the
script will give a suggestion of the code to add to this file. Make sure to use
the same ConceptSchem ID since it is needed to connect your provider and the
conceptscheme in the database.

For example, to insert this file:

.. code-block:: json

    [{"broader": [],
      "id": 1,
      "labels": [{"label": "The Larch",
                   "language": "en",
                   "type": "prefLabel"},
                  {"label": "De Lariks",
                   "language": "nl",
                   "type": "prefLabel"}],
      "matches": {"broad": [],
                   "close": [],
                   "exact": [],
                   "narrow": [],
                   "related": []},
      "member_of": [3],
      "narrower": [],
      "notes": [{"language": "en",
                  "note": "A type of tree.",
                  "type": "definition"}],
      "related": [],
      "subordinate_arrays": [],
      "type": "concept",
      "uri": "http://id.trees.org/1"},
     {"broader": [],
      "id": 2,
      "labels": [{"label": "The Chestnut",
                   "language": "en",
                   "type": "prefLabel"},
                  {"label": "De Paardekastanje",
                   "language": "nl",
                   "type": "altLabel"},
                  {"label": "la châtaigne",
                   "language": "fr",
                   "type": "altLabel"}],
      "matches": {"broad": [],
                   "close": [],
                   "exact": [],
                   "narrow": [],
                   "related": []},
      "member_of": [3],
      "narrower": [],
      "notes": [{"language": "en",
                  "note": "A different type of tree.",
                  "type": "definition"}],
      "related": [],
      "subordinate_arrays": [],
      "type": "concept",
      "uri": "http://id.trees.org/2"},
     {"id": 3,
      "labels": [{"label": "Bomen per soort",
                   "language": "nl",
                   "type": "prefLabel"},
                  {"label": "Trees by species",
                   "language": "en",
                   "type": "prefLabel"}],
      "member_of": [],
      "members": [1, 2],
      "notes": [],
      "superordinates": [],
      "type": "collection",
      "uri": "http://id.trees.org/3"}]

We run the following command:

.. code-block:: bash

    $ workon my_thesarus
    $ import_file --from my_thesaurus/data/trees.json --to sqlite:///my_thesaurus.sqlite --conceptscheme_label Trees

This will return output similar to this:

.. code-block:: bash

    sqlalchemy.engine.base.Engine SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    sqlalchemy.engine.base.Engine ()
    sqlalchemy.engine.base.Engine SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    sqlalchemy.engine.base.Engine ()
    sqlalchemy.engine.base.Engine BEGIN (implicit)
    sqlalchemy.engine.base.Engine INSERT INTO note (note, notetype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('A type of tree.', 'definition', 'en')
    sqlalchemy.engine.base.Engine INSERT INTO note (note, notetype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('A different type of tree.', 'definition', 'en')
    sqlalchemy.engine.base.Engine INSERT INTO conceptscheme (uri) VALUES (?)
    sqlalchemy.engine.base.Engine (None,)
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('Trees', 'prefLabel', 'nl')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('The Larch', 'prefLabel', 'en')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('De Lariks', 'prefLabel', 'nl')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('The Chestnut', 'prefLabel', 'en')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('De Paardekastanje', 'altLabel', 'nl')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('la châtaigne', 'altLabel', 'fr')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('Bomen per soort', 'prefLabel', 'nl')
    sqlalchemy.engine.base.Engine INSERT INTO label (label, labeltype_id, language_id) VALUES (?, ?, ?)
    sqlalchemy.engine.base.Engine ('Trees by species', 'prefLabel', 'en')
    sqlalchemy.engine.base.Engine INSERT INTO conceptscheme_label (conceptscheme_id, label_id) VALUES (?, ?)
    sqlalchemy.engine.base.Engine (11, 3548)
    sqlalchemy.engine.base.Engine INSERT INTO concept (type, concept_id, uri, conceptscheme_id) VALUES (?, ?, ?, ?)
    sqlalchemy.engine.base.Engine ('concept', 1, 'http://id.trees.org/1', 11)
    sqlalchemy.engine.base.Engine INSERT INTO concept (type, concept_id, uri, conceptscheme_id) VALUES (?, ?, ?, ?)
    sqlalchemy.engine.base.Engine ('concept', 2, 'http://id.trees.org/2', 11)
    sqlalchemy.engine.base.Engine INSERT INTO concept (type, concept_id, uri, conceptscheme_id) VALUES (?, ?, ?, ?)
    sqlalchemy.engine.base.Engine ('collection', 3, 'http://id.trees.org/3', 11)
    sqlalchemy.engine.base.Engine INSERT INTO concept_label (concept_id, label_id) VALUES (?, ?)
    sqlalchemy.engine.base.Engine ((2558, 3551), (2558, 3552), (2558, 3553), (2557, 3549), (2557, 3550), (2559, 3554), (2559, 3555))
    sqlalchemy.engine.base.Engine INSERT INTO concept_note (concept_id, note_id) VALUES (?, ?)
    sqlalchemy.engine.base.Engine ((2558, 3605), (2557, 3604))
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept
    WHERE concept.conceptscheme_id = ? AND concept.concept_id = ? AND concept.type IN (?)
    sqlalchemy.engine.base.Engine (11, 1, 'concept')
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept
    WHERE concept.conceptscheme_id = ? AND concept.concept_id = ? AND concept.type IN (?)
    sqlalchemy.engine.base.Engine (11, 2, 'concept')
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept
    WHERE concept.conceptscheme_id = ? AND concept.concept_id = ? AND concept.type IN (?)
    sqlalchemy.engine.base.Engine (11, 3, 'collection')
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept
    WHERE concept.conceptscheme_id = ? AND concept.concept_id = ?
    sqlalchemy.engine.base.Engine (11, 1)
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept, collection_concept
    WHERE ? = collection_concept.collection_id AND concept.id = collection_concept.concept_id
    sqlalchemy.engine.base.Engine (2559,)
    sqlalchemy.engine.base.Engine INSERT INTO collection_concept (collection_id, concept_id) VALUES (?, ?)
    sqlalchemy.engine.base.Engine (2559, 2557)
    sqlalchemy.engine.base.Engine SELECT concept.id AS concept_id_1, concept.type AS concept_type, concept.concept_id AS concept_concept_id, concept.uri AS concept_uri, concept.conceptscheme_id AS concept_conceptscheme_id
    FROM concept
    WHERE concept.conceptscheme_id = ? AND concept.concept_id = ?
    sqlalchemy.engine.base.Engine (11, 2)
    sqlalchemy.engine.base.Engine INSERT INTO collection_concept (collection_id, concept_id) VALUES (?, ?)
    sqlalchemy.engine.base.Engine (2559, 2558)
    sqlalchemy.engine.base.Engine COMMIT
    sqlalchemy.engine.base.Engine BEGIN (implicit)
    sqlalchemy.engine.base.Engine SELECT label.id AS label_id, label.label AS label_label, label.labeltype_id AS label_labeltype_id, label.language_id AS label_language_id
    FROM label JOIN conceptscheme_label ON label.id = conceptscheme_label.label_id
    WHERE label.label = ?
     LIMIT ? OFFSET ?
    sqlalchemy.engine.base.Engine ('Trees', 1, 0)
    sqlalchemy.engine.base.Engine SELECT conceptscheme.id AS conceptscheme_id, conceptscheme.uri AS conceptscheme_uri
    FROM conceptscheme, conceptscheme_label
    WHERE ? = conceptscheme_label.label_id AND conceptscheme.id = conceptscheme_label.conceptscheme_id
    sqlalchemy.engine.base.Engine (3548,)


    *** The import of the my_thesaurus/data/trees.json file with conceptscheme label 'Trees' to sqlite:///my_thesaurus.sqlite was successfull. ***

    To use the data in Atramhasis, you must edit the file my_thesaurus/skos/__init__.py.
    Add next lines:

    def includeme(config):
            TREES = SQLAlchemyProvider(
                    {'id': 'TREES', 'conceptscheme_id': 11},
                    config.registry.dbmaker
            )
            skosregis = config.get_skos_registry()
            skosregis.register_provider(TREES)

Just follow these instructions and edit your :file:`my_thesaurus/skos/__init__.py` like this:

.. code-block:: python

    # -*- coding: utf-8 -*-

    import logging
    log = logging.getLogger(__name__)
    
    from skosprovider.registry import Registry
    from skosprovider_sqlalchemy.providers import SQLAlchemyProvider


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')a

        TREES = SQLAlchemyProvider(
                {'id': 'TREES', 'conceptscheme_id': 11},
                request.db
        )
        registry.register_provider(TREES)

        return registry

Now your thesaurus has been successfully imported and is ready to be browsed,
expanded and edited.

SessionFactory
==============

You can change the default session factory in the __init__.py file.

.. code-block:: python

    # set default session factory
    from pyramid.session import SignedCookieSessionFactory
    atramhasis_session_factory = SignedCookieSessionFactory(settings['atramhasis.session_factory.secret'])
    config.set_session_factory(atramhasis_session_factory)
