.. _development:

Development
===========

General installation
--------------------

As with the demo site, we recommend installing Atramhasis in a virtual 
environment.

.. code-block:: bash    
    
    $ mkvirtualenv atramhasis_dev

To install a fully working development environment a pip requirements-dev.txt
file is provided. By passing this file to :command:`pip install -r` all 
requirements for Atramhasis and development of the software (Sphinx, py.test,
tox) will be installed.

The following step will help you get the python development environment up and
running. If also need to work on the javascript admin backend, please refer
to the admin module documentation.

.. code-block:: bash

    # Install dependencies
    $ pip install -r requirements-dev.txt
    # create or update database
    $ alembic upgrade head
    # insert sample data
    $ initialize_atramhasis_db development.ini
    # compile the Message Catalog Files
    $ python setup.py compile_catalog

Once you've executed these steps, you can run a development server. This uses
the standard pyramid server (`Waitress`_) and should not be used as-is in a
production environment.

.. code-block:: bash

    # run a local development server
    $ pserve --reload development.ini


Admin development
-----------------

To work on the admin part, you'll need `npm`_ and `bower`_ installed. Consult
your operating system documentation on how to install these. The following
instructions will assume you're running a recent Debian based Linux distribution.

.. code-block:: bash

    # install npm, bower and grunt-cli
    $ sudo apt-get install nodejs
    $ sudo apt-get install npm
    $ sudo npm install -g bower grunt-cli
    # install js dependencies using bower
    $ cd atramhasis/static/admin
    $ bower install
    # install dojo build tools
    $ npm install

These commands will install a couple of js libraries that Atramhasis uses in
:file:`/atramhasis/static/admin/src` and a set of tools to be able to generate
js builds. Builds are carried out through a simple `grunt`_ file:

.. code-block:: bash

   # Build a dojo distribution
   $ cd atramhasis/static/admin
   $ grunt -v build

This will create a build a place the resulting files in 
:file:`atramhasis/static/admin/dist`. The web application can be told to use
this build by setting `dojo.mode` in :file:`development.ini` to `dist`.

Contributing
------------

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
------------

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
.. _bower: http://bower.io/
.. _grunt: http://gruntjs.com
.. _waitress: http://waitress.readthedocs.org
