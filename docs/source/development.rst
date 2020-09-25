.. _development:

===========
Development
===========

Technology
==========

Atramhasis is a python_ webapplication that is being developed within the 
pyramid_ framework. Other major technologies used are sqlalchemy_ as the ORM 
and :term:`Jinja2` as the templating framework.

Client side the main technologies being used are Zurb Foundation and Dojo toolkit.

While Atramhasis is an editor for creating and editing :term:`SKOS` vocabularies,
it uses other libraries that are more geared towards using a vocabulary in an
application.

* skosprovider_: This library defines a 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>`. This 
  is an abstraction of usefull functionalities an application integrating 
  :term:`SKOS` needs. Different libraries can implement this interface for 
  different datasources. This allows decoupling the interface from the concrete
  implementation. Out of the box this comes with a simple 
  :class:`DictionaryProvider <skosprovider.providers.DictionaryProvider>` that
  serves a vocabulary based on a simple python :class:`dict` as datasource.
* skosprovider_sqlalchemy_: An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `SQLAlchemy <http://www.sqlalchemy.org>`_ backend. This allows
  using a RDBMS for reading, but also writing, :term:`SKOS` concepts.
* skosprovider_rdf_: An implemenation of the 
  :class:`~skosprovider.providers.VocabularyProvider` interface with an :term:`RDF`
  backend. Atramhasis uses this for exporting ConceptSchemes to RDF. It can 
  also be used to get an existing :term:`SKOS` vocabulary defined in RDF into
  Atramhasis.
* pyramid_skosprovider_: A library that integrates pyramid_ and skosprovider_.
  This libraries creates a :class:`skosprovider.registry.Registry` and makes it
  accessible through the :class:`pyramid.request.Request`. Is also exposes a 
  set of readonly :ref:`REST services <pyramidskosprovider:services>` on the 
  registered providers.
* skosprovider_getty_:
  An implemenation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  against the Linked Open Data vocabularies published by the Getty Research 
  Institute at `http://vocab.getty.edu <http://vocab.getty.edu>`_ such as the
  `Art and Architecture Thesaurus (AAT)` and the 
  `Thesaurus of Geographic Names (TGN)`.
* skosprovider_heritagedata_:
  An implementation of the
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` against
  the vocabularies published by EH, RCAHMS and RCAHMW at 
  `heritagedata.org <http://heritagedata.org>`_.

Atramhasis can easily be set up with a `Linked Data Fragments (LDF) <http://linkeddatafragments.org>`_ 
server. This server allows posing simple `triple pattern` queries of your dataset. 
Combined with a Linked Data Fragments client, similar functionalities to a 
traditional `SPARQL` endpoint can be achieved. Atramhasis facilitates the setup
of a Linked Data Fragments server by generating a suitable config file 
for the `Javascript server <https://github.com/LinkedDataFragments/Server.js>`_.
This server can use different backends. Out of the box, Atramhasis generates
Turtle files that can be used by the LDF server. It's also possible to configre
Atramhasis with a link to the rdf2hdt command (requires a separate
installation). In this case, everytime the conceptschemes are dumped to RDF, the
dump files are also written in :term:`HDT` format.

General installation
====================

We recommend installing Atramhasis in a virtual environment.

.. code-block:: bash    
    
    $ mkvirtualenv atramhasis_dev

To install a fully working development environment a pip requirements-dev.txt
file is provided. By passing this file to :command:`pip install -r` all 
requirements for Atramhasis and development of the software (Sphinx, py.test,
tox) will be installed.

The following step will help you get the python development environment up and
running. If you also need to work on the javascript admin backend, please refer
to the admin module documentation.

.. code-block:: bash

    # Install dependencies
    $ pip install -r requirements-dev.txt
    # create or update database
    $ alembic upgrade head
    # insert sample data
    $ initialize_atramhasis_db development.ini
    # generate first RDF download
    $ dump_rdf development.ini
    # compile the Message Catalog Files
    $ python setup.py compile_catalog

Once you've executed these steps, you can run a development server. This uses
the standard pyramid server (`Waitress`_) and should not be used as-is in a
production environment.

.. code-block:: bash

    # run a local development server
    $ pserve --reload development.ini


Admin development
=================

To work on the admin part, you'll need `npm`_ installed. Consult
your operating system documentation on how to install these. The following
instructions will assume you're running a recent Debian based Linux distribution.

.. code-block:: bash

    # install npm and grunt-cli
    $ sudo apt install nodejs
    $ sudo apt install npm
    $ sudo npm install -g grunt-cli
    # install js dependencies for public site using npm
    $ cd atramhasis/static
    $ npm install
    # install js dependencies for admin using npm
    $ cd atramhasis/static/admin
    $ npm install

These commands will install a couple of js libraries that Atramhasis uses in
:file:`/atramhasis/static/node_modules` and :file:`/atramhasis/static/admin/node_modules` and a set of tools to be able
to generate js builds. Builds are carried out through a simple `grunt`_ file:

.. code-block:: bash

   # Build a dojo distribution
   $ cd atramhasis/static/admin
   $ grunt -v build

This will create a build a place the resulting files in 
:file:`atramhasis/static/admin/dist`. The web application can be told to use
this build by setting `dojo.mode` in :file:`development.ini` to `dist`.

Frontend development
====================

When updating the frontend templates, you might want to add extra translations.
This can be done by placing {% trans %} tags in the templates

.. code-block:: html

    <h2>{% trans %}welcome_to{% endtrans %}</h2>

To update the message catalogs, do as follows:

.. code-block:: bash

    $ python setup.py extract_messages
    $ python setup.py update_catalog -l fr -i atramhasis/locale/atramhasis.pot -o atramhasis/locale/fr/LC_MESSAGES/atramhasis.po
    $ python setup.py update_catalog -l nl -i atramhasis/locale/atramhasis.pot -o atramhasis/locale/nl/LC_MESSAGES/atramhasis.po
    $ python setup.py update_catalog -l en -i atramhasis/locale/atramhasis.pot -o atramhasis/locale/en/LC_MESSAGES/atramhasis.po

Update the catalogs accordingly and run:

.. code-block:: bash

    $ python setup.py compile_catalog

You might also want to add a new translation. Suppose you want to add a German
translation.

.. code-block:: bash

    $ python setup.py init_catalog -l de -i atramhasis/locale/atramhasis.pot -o atramhasis/locale/de/LC_MESSAGES/atramhasis.po

Edit :file:`atramhasis/locale/do/LC_MESSAGES/atramhasis.po` and add the necessary
translations. Just as with updating the catalogs, you need to recompile them.

.. code-block:: bash

    $ python setup.py compile_catalog

At this moment, Atramhasis will still only show the default languages in it's
language switcher. If you want to add you new language, you need to edit your
:file:`development.ini` (or similar file). Look for the line that says 
`available_languages` and add your locale identifier.

.. code-block:: ini

    available_languages = en nl fr de

After restarting your server you will now have the option of switching to
German.

Running a Linked Data Fragments server
======================================

If you want to add a `Linked Data Fragments <http://linkeddatafragments.org>`_
server, Atramhasis makes it easy for you. First you need to decide if you want
to run the server with :term:`HDT` files. If not, you can always use raw `Turtle`
files, but be aware that the :term:`HDT` files offer much better performance.

If you want to use :term:`HDT` files, please install `hdt-cpp`. Be aware that
you might have to download the source files and compile them yourself. Once
you have done so, add the rdf2hdt command to your development.ini file.
Supposing you installed it in :file:`/opt/hdt-cpp/hdt-lib/tools/rdf2hdt`:

.. code-block:: ini

    # Location of rdf2hdt executable
    atramhasis.rdf2hdt = /opt/hdt-cpp/hdt-lib/tools/rdf2hdt

Now, whenever Atramhasis creates rdf dumps it will also create :term:`HDT`
files. If you do not have :command:`rdf2hdt` installed, you will still have
`Turtle` datadumps that can be used by the LDF-server.

.. code-block:: bash

    $ dump_rdf development.ini

Now you're ready to generate the configuration for the LDF server. Out of the
box this file will be generated in the same directory your
:file:`development.ini` is located in, but you can override this in your ini
file by setting `atramhasis.ldf.config_location` or you can pass this on the
command line

.. code-block:: bash

    # Generate config
    $ generate_ldf_config development.ini
    # Generate config and override config_location
    $ generate_ldf_config development.ini -l /opt/my/ldf/server

Now you're ready to run your LDF server. First we need to install it. It
requires `Node.js 4.0` or higher and should run on `OSX` and `Linux`. Please
refer to the LDF server documentation for troubleshooting.

.. code-block:: bash

    # Install ldf-server
    $ [sudo] npm install -g ldf-server
    # Run ldf-server
    $ ldf-server ldf_server_config.json

Now you have an LDF server running at `http://localhost:3000`. Browse there and
have fun!

When deploying Atramhasis with an LDF server in production, we recommend runnig
both behind eg. `nginx`. In case you want to do this, you might run Atramhasis
on port `6543` and LDF server on port `3000`, but serve both through `nginx`.
You can easily do this by setting the `atramhasis.ldf.baseurl` in your ini file.
Suppose you want to server both on the host `demo.atramhasis.org` with
Atramhasis as the root of your domain and the LDF server at `/ldf`. In this
case, set `atramhasis.ldf.baseurl` to `http://demo.atramhasis.org/ldf`.


Contributing
============

Atramhasis is being developed as open source software by the 
`Flanders Heritage Agency`_. All development is done on the agency's 
`Github page for Atramhasis`_.

Since we place a lot of importance of code quality, we expect to have a good 
amount of code coverage present and run frequent unit tests. All commits and
pull requests will be tested with `Travis-ci`_. Code coverage is being 
monitored with `Coveralls`_.

Locally you can run unit tests by using `pytest`_ or `tox`_. Running pytest 
manually is good for running a distinct set of unit tests. For a full test run, 
tox is preferred since this can run the unit tests against multiple versions of
python.

.. code-block:: bash

    # Run unit tests for all environments 
    $ tox
    # No coverage
    $ py.test 
    # Coverage
    $ py.test --cov atramhasis --cov-report term-missing
    # Only run a subset of the tests
    $ py.test atramhasis/tests/test_views.py

Every pull request will be run through Travis-ci_. When providing a pull 
request, please run the unit tests first and make sure they all pass. Please 
provide new unit tests to maintain 100% coverage. If you send us a pull request
and this build doesn't function, please correct the issue at hand or let us 
know why it's not working.

Distribution
============

For building a distribution use the prepare command before the distribution command.
This will update the requirement files in the scaffolds.

.. code-block:: bash

    $ python setup.py prepare sdist


.. _Flanders Heritage Agency: https://www.onroerenderfgoed.be
.. _Github page for Atramhasis: https://github.com/OnroerendErfgoed/atramhasis
.. _Travis-ci: https://travis-ci.org/OnroerendErfgoed/atramhasis
.. _Coveralls: https://coveralls.io/r/OnroerendErfgoed/atramhasis
.. _pytest: http://pytest.org
.. _tox: http://tox.readthedocs.org
.. _npm: https://www.npmjs.org/
.. _grunt: http://gruntjs.com
.. _waitress: http://waitress.readthedocs.org
.. _python: https://wwww.python.org
.. _pyramid: http://www.pylonsproject.org/
.. _sqlalchemy: http://www.sqlalchemy.org
.. _skosprovider: http://skosprovider.readthedocs.org
.. _skosprovider_sqlalchemy: http://skosprovider-sqlalchemy.readthedocs.org
.. _skosprovider_rdf: http://skosprovider-rdf.readthedocs.org
.. _pyramid_skosprovider: http://pyramid-skosprovider.readthedocs.org
.. _skosprovider_getty: http://skosprovider-getty.readthedocs.org
.. _skosprovider_heritagedata: http://skosprovider-heritagedata.readthedocs.org
