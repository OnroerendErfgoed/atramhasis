.. _running_the_demo:

Running a demo site
===================

Atramhasis comes with a demo site include. This allows you to quickly evaluate
and inspect the software. To get started, just download Atramhasis from pypi and
install it. We recommend doing this in a virtualenvironment.

.. code-block:: bash    
    
    $ mkvirtualenv atramhasis_demo
    $ pip install -U atramhasis


Once Atramhasis is installed, you can call upon a pyramid scaffold to generate
the demo site.

.. code-block:: bash    
    
    $ pcreate -s atramhasis_demo atramhasis_demo
    $ cd atramhasis_demo

This creates a local demo package you can run with just a few more commands:

.. code-block:: bash    

    # create or upgrade database
    $ alembic upgrade head
    # setup
    $ python setup.py develop
    # intialize sample data
    $ initialize_atramhasis_db development.ini
    # start server
    $ pserve development.ini

The Atramhasis demo instance is now running on your localhost at post 6543.
