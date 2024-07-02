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

Requirements
------------

*   Python 3.9+
*   npm

Usage
-----

1.  Create a virtual environment and install requirements

    .. code-block:: bash

        # create a new virtual environment for the project, fe python -m venv $HOME/.virtualenvs/my_atramhasis
        $ VENV_PATH=$HOME/Envs
        $ python -m venv $VENV_PATH/my_atramhasis
        $ . $VENV_PATH/my_atramhasis/bin/activate
        # Make sure pip and pip-tools are up to date
        $ pip install --upgrade pip pip-tools
        $ pip install --upgrade cookiecutter

2.  Use cookiecutter to generate an atramhasis project

    .. code-block:: bash

        $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory cookiecutters/scaffold

3.  Install requirements

You can opt to generate requirements*.txt files from the pyproject.toml file and install the dependencies,
or you can install them directly from the pyproject.toml file.

*Using requirements*.txt files*:

    .. code-block:: bash

        $ cd <root of newly from scaffold created project>
        # Generate requirements files from the existing pyproject.toml
        $ PIP_COMPILE_ARGS="-v --strip-extras --no-header --resolver=backtracking --no-emit-options --no-emit-find-links";
        # Generate requirements files for a production environment
        $ pip-compile $PIP_COMPILE_ARGS;
        # Generate requirements files for a development environment
        $ pip-compile $PIP_COMPILE_ARGS --all-extras -o requirements-dev.txt;

        # Install dependencies
        $ pip-sync requirements-dev.txt
        # Install the new project in editable mode
        $ pip install -e .

    Note that pip-sync will uninstall all packages that are not listed in the requirements. The package cookiecutter
    is no longer needed and will be uninstalled when executing pip-sync.

*Using pyproject.toml*:

    .. code-block:: bash

        $ cd <root of newly from scaffold created project>
        # Install the new project in editable mode via argument -e
        # Optional: Include [dev] to install the development dependencies
        $ pip install -e .[dev]

4.  Setup database

    .. code-block:: bash

        $ alembic upgrade head

5.  Run server

    .. code-block:: bash

        $ pserve development.ini



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

    $ alembic init alembic

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
    and multiple heads when upgrading atramhasis in the future and this is
    ill-advised

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


.. _creating_conceptschemes:

Creating conceptschemes
-----------------------

Atramhasis is now running but does not contain any conceptschemes. A conceptscheme
is a single set of concepts and collections, also known sometimes as a thesaurus or 
vocabulary. All concepts you describe in Atramhasis must be part of exactly one 
conceptscheme. Every conceptscheme is handled by a provider. The conceptscheme is 
the domain specific knowledge you are trying to describe, the provider contains 
some logic on how to display this knowledge and handle it. We have split the two for 
various, mostly technical, reasons. You might want to have staff with IT experience
to create and maintain the providers, while the conceptschemes might be maintained 
by domain experts you do not want to burden with technical decisions. Atramhasis 
makes this possible.

.. warning::

    Prior to version 2.0.0, creating conceptschemes and providers required manual
    interventions and writing a little bit of code. This has changes significantly.
    If you have an older installation, please make sure to read `upgrading_providers`_ 
    before upgrading.

Adding a new provider through the UI
....................................

The easiest way to register a new provider is to use the UI. Surf to 
`http://localhost:6543/admin`. On your right you will see the menu where most
of the interaction takes place. Bottom right, there's a button labelled `Providers`.
Pressing this button takes you into a menu that allows you to configure providers.

.. image:: images/admin_providers_list.png
  :alt: The providers list dialog

This dialog lists all providers currently registerd in your Atramhasis instance. 
Most of these will be regular SQLAlchemyProviders that will serve your conceptschemes
and their concepts and collections. The dialog also lists other providers that cannot
be managed through the UI. These are *external* providers that provide data from 
another source, such as the Getty `Art and Architecture Thesaurus (AAT)`. See 
`external_providers`_ for more information on how to do this. For now it's enough
to understand there can be some providers that can't be edited through the UI.

To add a new provider, press the `Add a provider` button. This will add a new 
provider and create the associated conceptscheme. Once the provider is created,
the conceptscheme can be edited through the UI for conceptschemes. To create a 
provider the following information needs to be provided:

* `id`: An identifier for the provider, can be a string or a number, eg. 
  `heritagetypes` or 5. When left blank, an id will be assigned by Atramhasis
  equal to the DB identifier of the conceptscheme. The provider id is used
  in constructing URL's for the application and will be visible in your final 
  document URL.
* `conceptscheme uri`: A URI for the conceptscheme. This should be a unique URI
  that resolves to the conceptscheme's URL in Atramhasis. If you are creating a 
  thesaurus of colours at http://data.me.org/colours, your `id` might be `colours`
  and the URI might be http://id.me.org/colours. This URI should redirect to 
  `http://data.me.org/colours`. Another common option is to use 
  `http://data.me.org/colours#id` as the URI for your conceptscheme.
* `uri pattern`: A pattern that will be used by a :class:`~skosprovider.uri.UriGenerator` 
  to generate URI's for new concepts and collections added to your conceptscheme. 
  The pattern looks like a http URI with the marker `%s` as a placeholder for 
  your concept or collection id. Continuing our example, this could be 
  `http://id.me.org/colours/%s` or `http://data.me.org/colours/%s#id`.
* `default language`: The default language of the provider. When a concept is 
  requested, a single label is always returned for ease of display. Normally 
  this is determined from browser settings or cookies, but if none of these are
  present, Atramhasis will try this language. Should generally be set to the 
  main or prevalent language in your thesaurus. When not present, Atramhasis
  falls back to English as the lingua franca.
* `force display language`: Even though the client can generally choose which 
  language a concept or tree view should be displayed in, there are times when
  it's handy to force the display language. This has been used before for biological 
  taxonomies where you might always want to display the name in Latin,
  even though there's a more local name available. See `force_display_label_language`_ 
  for more information. For most thesauri this will be blank.
* `ID Generation Strategy`: Every concept or collection needs a unique 
  identifier. This identifier is used in generating URI's. There are three
  possible strategies for generating ID's:

  * `numeric (default)`: Before Atramhasis 2.0.0 this was the only option. 
    It generates a numeric id based on the current highest id in the conceptscheme.
  * `guid`: Generate a GUID as identifier for your concept or collection.
  * `manual`: No identifier is generated by Atramhasis, but the user
    is required to generate them manually. Allows for full control
    over ID's and URI's, at the cost of a little more work.

* `subject`: Add a certain tag to a provider. Currently there are two
  recognised tags:
  
  * `external`: Must be added to an external provider, in code.
  * `hidden`: Used to obfuscate a conceptscheme. The scheme will not be
    shown in the Atramhasis UI, except when the URL's of concepts or
    collections are requested. This allows having a conceptscheme that
    can be used in applications, but is not the main focus of your 
    Atramhasis instance. See `hidden_providers`_ for more information.

* `expand strategy`: One of the features of Atramhasis is quickly 
  determining all the narrower concepts of a certain concept, mainly to 
  be used in querying other systems. There are two options:

  * `recurse`: Use recursive queries to determine the narrower concepts.
    For large vocabularies this generally requires good caching.
  * `visit`: Query a special visitation table that is pre-computed. Will
    be much more performant, but requires that the table is recomputed
    regulary.
  
  When in doubt, use recurse and pay attention to caching.


After filling out the required fields and pressing `Save`, a provider and
an associated conceptscheme will be created. The conceptscheme will be very 
barebones, so it's recommended to add extra labels, notes and sources to
the conceptscheme to inform end users.

.. warning::

   The :class:`~skosprovider.uri.UriGenerator` that you configure only generates
   URI's when creating new concepts or collections. When importing existing
   vocabularies, please be sure to create the URI's before or during import
   (possbily by using a relevant generator yourself).

Adding a new provider through the REST API
..........................................

Apart from using the UI, it's also possible to create a provider through the 
REST API, by POSTing to the `http://localhost:6543/providers` endpoint to have 
the server assign an id or by PUTTing to the `http://localhost:6543/providers/<id>` 
endpoint to assign your own id, using the following payload:

.. code-block:: json

    {
        "id":"CHEESE",
        "conceptscheme_uri":"https://id.python.org/cheese",
        "uri_pattern":"https://id.python.org/cheese/%s",
        "subject":[],
        "id_generation_strategy":"NUMERIC",
        "expand_strategy":"recurse",
        "default_language":"en",
        "force_display_language":""
    }

If all goes well, you'll be greeted with a `201 Created` status and your new
provider and conceptscheme will be available through the UI.

More information about the Atramhasis API can be found at the 
`http://localhost:6543/api_doc` endpoint of your Atramhasis instance 
or at `https://thesaurus.onroerenderfgoed.be/api_doc`.


Creating concepts and collections
---------------------------------

You can now start creating concepts and collections by
going to the admin interface at `http://localhost:6543/admin`.

.. _hidden_providers:

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

To set this, set the `force_display_language` attribute of your provider, either
through the UI or the REST interface (`creating_conceptschemes`_). Set it to a 
language supported by the provider (there's little sense to setting it to a 
language that isn't present in the vocabulary). Now Atramhasis will try serving 
concepts from this provider with this language. All labels will still be shown, 
but the page title or current label will be set to the selected language as much 
as possible. The normal language determination mechanisms will keep on working, 
so if the concept has no label in the requested language, Atramhasis will fall 
back on other labels present.

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
:file:`my_thesaurus/__init__.py`.

.. code-block:: python

    config.override_asset(
        to_override='atramhasis:templates/welcome.jinja2',
        override_with='my_thesaurus:templates/my_welcome.jinja2'
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

.. _sitemap:

Sitemap
=======

Since Atramhasis 0.7.0 it's possible to generate a sitemap. It consists of a
set of files (one per conceptscheme and an index file) you can submit to a
search engine. It will help it index your thesaurus as efficiently as possible. 

You can generate the sitemap using the following commands:

.. code-block:: bash

    # remove any existing sitemaps
    $ rm my_thesaurus/static/_sitemaps/*
    $ sitemap_generator development.ini

The sitemap index xml will be visible at the root of your webserver, eg. 
`<http://localhost:6543/sitemap_index.xml>`_. Depending on how often you edit
conceptschemes, concepts or collections it's a good idea to make this into a
cron job. When recreating the sitemap it is best practice to remove
existing files from the static/_sitemap directory. If the directory is not empty 
the script will overwrite existing sitemaps, but unused sitemaps will be retained. 
Unless the  --no-input flag is used, the script wil ask the user to press [enter] before 
overwriting existing files. The sitemap index will always contain links to all 
the files (used and unused).

Since a sitemap needs to contain abolute URL's, the script needs to know where
the application is being hosted. This can be controlled with a setting
`atramhasis.url` in the application's ini file. Set this to the root of your
webapplication, eg. `http://my.thesaurus.org` (no trailing slash needed).

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


Adding Analytics
================

Out of the box, it's very easy to add any analytics integration to Atramhasis.
All you need to do is add your tracking snippet to :file:`development.ini`.

Example code to add Google Analytics tracking:

.. code-block:: ini

    # Enter your tracking snippet
    tracking_snippet = <!-- Google Analytics -->
        <script type="text/javascript">
        (function(i,s,o,g,r,a,m){i["GoogleAnalyticsObject"]=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,"script","//www.google-analytics.com/analytics.js","ga");

        ga("create", "some_key", "auto");
        ga("set", "forceSSL", true);
        ga("send", "pageview");
        </script>
        <!-- End Google Analytics -->

Another example to add Plausible Analytics:

.. code-block:: ini

    # Enter your tracking snippet
    tracking_snippet = <script defer data-domain="your.domain.com"
        src="https://your.plausibleinstance.com/js/script.js">
        </script>


.. _external_providers:

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

To enable all this power, you need to configure an external provider in your
application. Continuing with our :ref:`example project <own_project>`, we need
to go and edit a :file:`my_thesaurus/skos/__init__.py`. In this file you need
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

Once this is done, we need to instantiate the provider within the `create_registry`
function and register it with the :class:`skosprovider.registry.Registry`. 
By adding the `external` subject to the provider, we let Atramhasis know that 
this is not a regular, internal provider that can be stored in our database, 
but a special external one that can only be used for making matches. As such, 
it will not be present and visible to the public among your regular vocabularies.

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
    from skosprovider_getty.providers import AATProvider
    from atramhasis.skos import register_providers_from_db


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        AAT = AATProvider(
            {
                'id': 'AAT',
                'subject': ['external']
            }
        )

        registry.register_provider(AAT)

        register_providers_from_db(registry, request.db)

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

- When importing from an RDF vocabulary, the id will be read from a `dc` or
  `dcterms` `identifier` property if present. If you have local identifiers,
  please make sure to add them using this property. If not, your concept and
  collections will use their URI's as id.
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

    usage: import_file.py [-h] [--to conn_string] [--conceptscheme-label CS_LABEL]
                          [--conceptscheme-uri CS_URI]
                          [--create-provider | --no-create-provider]
                          [--provider-id PROVIDER_ID]
                          [--id-generation-strategy {numeric,guid,manual}]
                          input_file uri_pattern

    Import file to a database

    positional arguments:
      input_file            local path to the input file
      uri_pattern           URI pattern input for the URIGenerator

    options:
      -h, --help            show this help message and exit
      --to conn_string      Connection string of the output database
      --conceptscheme-label CS_LABEL
                            Label of the conceptscheme
      --conceptscheme-uri CS_URI
                            URI of the conceptscheme
      --create-provider, --no-create-provider
                            An optional parameter if given a provider is created.
                            Use --no-create-provider to not create a provider
                            (default: True)
      --provider-id PROVIDER_ID
                            An optional string (eg. ERFGOEDTYPES) to be assigned
                            to the provider id. If not specified, assign the
                            conceptscheme id to the provider id
      --id-generation-strategy {numeric,guid,manual}
                            URI pattern input for the URIGenerator

    example: import_file.py atramhasis/scripts/my_file urn:x-skosprovider:trees:%s
    --to sqlite:///atramhasis.sqlite --conceptscheme-label Labels --conceptscheme-
    uri urn:x-skosprovider:trees --create-provider --provider-id ERFGOEDTYPES
    --id-generation-strategy numeric


The `input_file` is a positional required argument and details where the file 
you want to import is located, for example :file:`my_thesaurus/data/trees.json`. 
It is relative to your current location.

The `uri_pattern` is a positional required argument that details the URI pattern 
that will be used by the provider to create concept and collection URI's.

The `to` argument contains the connection string of output database. Only
PostGreSQL and SQLite are supported. The structure is either
`postgresql://username:password@host:port/db_name` or
either `sqlite:///path/db_name.sqlite`. The default value is `sqlite:///atramhasis.sqlite`.

The data is loaded in a :class:`~skosprovider_sqlalchemy.models.ConceptScheme`. With a 
:class:`~skosprovider_rdf.providers.RDFProvider` the conceptscheme can be present
in the RDF file. The other providers can specify it on the command line
through the `conceptscheme_label` argument. If no `conceptscheme_label` is present,
the default label is the name of the file.

Once the data is loaded in the database, your conceptscheme and provider will 
be ready, unless you chose the `--no-create-provider` option. This is rarely what 
you want and is only useful if you are doing some manual interventions in your 
database.

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
    $ import_file my_thesaurus/data/trees.json <uri-pattern> --to sqlite:///my_thesaurus.sqlite --conceptscheme_label Trees

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

.. _upgrading_providers:
   
Updating an older installation of Atramhasis
============================================

If you are running an older installation of Atramhasis, it's important you 
reconfigure how providers are created. While they were created in pre-2.0.0
version by writing a little bit of code, since 2.0.0 they are created 
through the UI or the REST service and stored in the database. Run the
following command:

.. code-block:: bash

   $ workon my_thesaurus
   $ migrate_sqlalchemy_providers --setings_file development.ini

After running this command, all providers will be present in the DB and
you can safely delete some code in the :file:`my_thesaurus/skos/__init__.py`. 
You should edit you `create_registry` function. Where you would previously 
have instantiated all SQLAlchemyProviders in this function, you need to remove 
them and replace them with a call to 
:func:`~atramhasis.skos.create_providers_from_db`. Any external providers
you registered, such as AAT providers, should still be configured
through code in this file. Your final code should looks somewhat like this:

.. code-block:: python

    # -*- coding: utf-8 -*-

    import logging
    log = logging.getLogger(__name__)

    from skosprovider.registry import Registry
    from skosprovider_getty.providers import AATProvider
    from atramhasis.skos import register_providers_from_db


    def create_registry(request):
        # create the SKOS registry
        registry = Registry(instance_scope='threaded_thread')

        AAT = AATProvider(
            {
                'id': 'AAT',
                'subject': ['external']
            }
        )

        registry.register_provider(AAT)

        # Load all configured providers from the db
        register_providers_from_db(registry, request.db)

        return registry


Application settings
====================
These are settings you can use to change the atramhasis behaviour.
When a setting is marked with DEFAULT then writing the setting is optional.
When a setting is marked with REQUIRED then it is strongly advised to fill in the
setting. Skipping these may not prevent the application from starting, but some
functionality might fail to run properly.

.. code-block:: ini

    [app:main]
    use = egg:my_app

    pyramid.default_locale_name = nl

    # DEFAULT - If you wish to add your own values you should append to these values
    jinja2.extensions =
        jinja2.ext.do
    # DEFAULT - If you wish to add your own values you should append to these values
    jinja2.filters =
        label_sort = atramhasis.utils.label_sort

    available_languages = en nl it

    # REQUIRED
    sqlalchemy.url = sqlite:///test.db
    # sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/atramhasis_test

    # DEFAULT
    skosprovider.skosregistry_location = request
    # DEFAULT
    skosprovider.skosregistry_factory = tests.create_registry

    # DEFAULT - cache which caches the data used for /conceptschemes/{scheme_id}/tree
    cache.tree.backend = dogpile.cache.memory
    cache.tree.arguments.cache_size = 5000
    cache.tree.expiration_time = 7000

    # DEFAULT - cache which caches the data used for /labeltypes and /notetypes
    cache.list.backend = dogpile.cache.memory
    cache.list.arguments.cache_size = 5000
    cache.list.expiration_time = 7000

    # REQUIRED - Filesystem location to dump exports
    atramhasis.dump_location = path/to/folder

    # REQUIRED - Assume an LDF server is present?
    atramhasis.ldf.enabled = True

    # External url of the LDF server
    atramhasis.ldf.baseurl = http://demo.atramhasis.org/ldf

    # DEFAULT empty list
    layout.focus_conceptschemes =
      HERITAGETYPE
      PERIOD
      GEOGRAPHY
      MATERIALS

    # DEFAULT - Run dojo from source (src) or distribution (dist)
    dojo.mode = dist

    # The Twitter @username the card should be attributed to.
    twitter.site =

    # Enter your tracking snippet
    tracking_snippet =