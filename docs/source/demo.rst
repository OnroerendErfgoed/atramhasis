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

    # setup
    $ pip install -r requirements-dev.txt
    $ python setup.py develop
    # create or upgrade database
    $ alembic upgrade head
    # intialize sample data
    $ initialize_atramhasis_db development.ini
    # compile translations
    $ python setup.py compile_catalog
    # start server
    $ pserve development.ini

The Atramhasis demo instance is now running on your localhost at port 6543. To
reach it, open your browser and surf to the address `<http://localhost:6543>`_.

You will be greeted by the Atramhasis front page. From this page you can start
searching and browsing the thesauri. You can also start editing the thesauri
by surfing to `<http://localhost:6543/admin>`_. The demo instance requires that
you login to access the admin module. We've provided a login mechanism using
`Mozilla Persona <http://www.mozilla.org/en-US/persona/>`_ for the demo. If you 
want to run Atramhasis in a production environment, you can easily replace the 
security module by another one. This enables you to use the security mechanisms 
(eg. LDAP, Active Directory, a custom users database, ...) that your 
organisation requires. Please consult the documentation on :ref:`security` 
customisation for further information on this topic.
