.. _development:

Development
===========

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

To install a fully working development environment a pip requirements-dev.txt
file is provided. By passing this file to :command:`pip install -r` all 
requirements for Atramhasis and development of the software (Sphinx, py.test,
tox) will be installed.

.. code-block:: bash

    # Install dependencies
    $ pip install -r requirements-dev.txt
    # Run unit tests for all environments 
    $ tox
    # No coverage
    $ py.test 
    # Coverage
    $ py.test --cov atramhasis --cov-report term-missing
    # Only run a subset of the tests
    $ py.test atramhasis/tests/test_views.py
    # create or update database
    $ alembic upgrade head
    # insert sample data
    $ initialize_atramhasis_db development.ini
    # compile the Message Catalog Files
    $ python setup.py compile_catalog

Every pull request will be run through Travis-ci_. When providing a pull 
request, please run the unit tests first and make sure they all pass. Please 
provide new unit tests to maintain 100% coverage. If you send us a pull request
and this build doesn't function, please correct the issue at hand or let us 
know why it's not working.

.. _Flanders Heritage Agency: https://www.onroerenderfgoed.be
.. _Github page for Atramhasis: https://github.com/OnroerendErfgoed/atramhasis
.. _Travis-ci: https://travis-ci.org/OnroerendErfgoed/atramhasis
.. _Coveralls: https://coveralls.io/r/OnroerendErfgoed/atramhasis
.. _pytest: http://pytest.org
.. _tox: http://tox.readthedocs.org
