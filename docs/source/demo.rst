.. _running_the_demo:

====
Demo
====

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
    # download and install client side libraries
    $ cd atramhasis_demo/static
    $ bower install
    $ cd admin
    $ bower install
    $ cd ../../..
    # create or upgrade database
    $ alembic upgrade head
    # intialize sample data
    $ initialize_atramhasis_db development.ini
    # compile translations
    $ python setup.py compile_catalog
    # generate full RDF dumps (not necessary for basic functionality)
    $ dump_rdf development.ini
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


Running a demo site on Heroku
=============================

This section will tell you how to deploy an Atramhasis demo (or your own implementation) in the cloud.
We'll use `Heroku <https://www.heroku.com/>`_, since this provider allows for a free Python instance
(dyno) with a limited Postgresql database.

Create an account on Heroku and make sure you have Heroku Toolbelt installed. Prepare your local Heroku `setup <https://devcenter.heroku.com/articles/getting-started-with-python#set-up>`_


.. note::

    More information on running Python apps on Heroku can be found on the `Heroku dev center <https://devcenter.heroku.com/articles/getting-started-with-python#introduction>`_.

Atramhasis scaffold
-------------------

Create an Atramhasis scaffold (if you want to deploy an existing scaffold, skip this step)

.. code-block:: bash

    $ mkvirtualenv atramhasis_heroku
    $ pip install -U atramhasis
    $ pcreate -s atramhasis_demo atramhasis_heroku
    $ cd atramhasis_heroku

Git repository
--------------

Make sure your atramhasis_heroku folder is a git repository.

.. code-block:: bash

    $ git init
    $ git add .
    $ git commit -m "initial commit"

requirements.txt
----------------

Update the requirements.txt file, make sure it contains a reference to atramhasis and to waitress.

.. note::

    waitress has to be in the requirements.txt file for our Heroku deployment, requirements-dev.txt will be ignored.

Procfile
--------

Generate ``Procfile`` with the following command.

.. code-block:: bash

    $ echo "web: ./run" > Procfile

run file
--------

Create ``run`` with the following content.

.. code-block:: bash

    #!/bin/bash
    set -e
    python setup.py develop
    python runapp.py

.. note::

    Make sure to ``chmod +x run`` before continuing. The ``develop`` step is
    necessary because the current package must be installed before Paste can
    load it from the INI file.

runapp.py
---------

Create a ``runapp.py`` file.

.. code-block:: python

    import os

    from paste.deploy import loadapp
    from waitress import serve

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app = loadapp('config:production.ini', relative_to='.')

        serve(app, host='0.0.0.0', port=port)


.. note::

    After creating the necessary files, commit them in your local git repository

Initialize the Heroku stack
---------------------------

.. code-block:: bash

    $ heroku create

Deploy to Heroku
----------------

To deploy a new version, push it to Heroku.

.. code-block:: bash

    $ git push heroku master

Postgresql
----------

Attach an Heroku Postgres add-on to your application

.. code-block:: bash

   $ heroku addons:add heroku-postgresql:hobby-dev

It can take a couple of minutes before your db is ready. You can wait for it to be ready
using this command.

.. code-block:: bash

    $ heroku pg:wait

When ready, check the connection url and copy paste it into your production.ini file

.. code-block:: bash

    $ heroku config | grep HEROKU_POSTGRESQL

Also change the alembic.ini file to check your production.ini file instead of development.ini

.. code-block:: bash

    ini_location = %(here)s/production.ini

Make sure to commit everything and push it to Heroku

.. code-block:: bash

    $ git commit -a
    $ git push heroku master

.. note::

    More info on `provisioning a database <https://devcenter.heroku.com/articles/heroku-postgresql>`_


Preparing the app
-----------------

Open a remote console on your app

.. code-block:: bash

    $ heroku run bash

This will start a console inside your remote Python virtualenv, so you can use all your libraries.

Run the commands to prepare your application

.. code-block:: bash

    $ python setup.py develop
    $ alembic upgrade head
    $ initialize_atramhasis_db production.ini
    $ python setup.py compile_catalog
    $ dump_rdf production.ini

.. note::

    Close the remote console!

Run the app
-----------

Run your app by starting one worker

.. code-block:: bash

    $ heroku scale web=1

Check to see if your app is running.

.. code-block:: bash

    $ heroku ps

Take a look at the logs to debug any errors if necessary.

.. code-block:: bash

    $ heroku logs -t

Your app should now be available on the application url.
