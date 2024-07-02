.. _running_the_demo:

====
Demo
====

Running a demo site with Cookiecutter
=====================================

Checking a working instance of the Atramhasis can be done at `the Flanders
Heritage Thesaurus <https://thesaurus.onroerenderfgoed.be>`_ or by running a
demo yourself. This allows you to quickly evaluate and inspect the software. 
This can be done through the `cookiecutter` package.


1.  Create a virtual environment and install requirements

.. code-block:: bash

    # create a new virtual environment for the project, fe python -m venv $HOME/.virtualenvs/atramhasis_demo
    # Change directory into your newly created project if not already there.
    $ python -m venv atramhasis_demo
    $ . atramhasis_demo/bin/activate
    # Make sure pip and pip-tools are up to date
    $ pip install --upgrade pip pip-tools
    $ pip install --upgrade cookiecutter

2.  Use cookiecutter to generate an demo project

.. code-block:: bash

    # Change the ATRAMHASIS_PATH to the path where your atramhasis project is located
    $ ATRAMHASIS_PATH=$HOME/dev/atramhasis
    $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory $ATRAMHASIS_PATH/cookiecutters/demo

Running this command will ask a few questions. Just accept the default answers,
unless you want to give your project a different name. After the
cookiecutter command, there should be a directory with the name of your
project (default: atramhasis_demo). Now enter this directory to start updating your virtual environment.


3.  Install requirements

.. code-block:: bash

    # Change directory into your newly created project
    $ cd atramhasis_demo
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

Note that pip-sync will uninstall all packages that are not listed in the requirements.
If you started from an existing virtualenv and you have packages in your virtualenv that
you want to keep or need, you should either reinstall them afterwards or use the
pip install command as follows:

.. code-block:: bash

    # Install dependencies
    $ pip install -r requirements-dev.txt
    # Install the new project in editable mode
    $ pip install -e .


4.  Setup database

Now it's time to setup our database (a simple SQLite database) and add some
testdata:

.. code-block:: bash

    $ alembic upgrade head
    # fill the database with data
    $ initialize_atramhasis_db development.ini

5.  Create RDF dumps

Optionally, we can create RDF dumps, but this is not necessary for basic
functionality:

.. code-block:: bash

    $ dump_rdf development.ini

6.  All we need now are some frontend dependencies:

.. code-block:: bash

    $ cd atramhasis_demo/static
    $ npm install

7.  Run server

.. code-block:: bash

    $ cd ../..
    # start server
    $ pserve development.ini


The Atramhasis demo instance is now running on your localhost at port 6543. To
reach it, open your browser and surf to the address `<http://localhost:6543>`_.

You will be greeted by the Atramhasis front page. From this page you can start
searching and browsing the thesauri. You can also start editing the thesauri
by surfing to `<http://localhost:6543/admin>`_. The demo instance does not
requires you to login to access the admin module. If you
want to run Atramhasis in a production environment, you can easily write your
own security module. This enables you to use the security mechanisms
(eg. LDAP, Active Directory, a custom users database, ...) that your
organisation requires. Please consult the documentation on :ref:`security`
customisation for further information on this topic.

Running a demo site with Docker
===============================

.. warning::

    This older documentation, written for a previous version, and probably
    doesn't work anymore.

There is a `Docker image <https://hub.docker.com/r/atramhasis/demo/>`_ 
available that allows you to quickly get a demo instance up and running. 
The Docker image contains the demo application and the LDF server. 

After installing Docker for your operating system, you 
can simply pull the image and run a container. Once you've
executed the following commands, you should be able to 
visit the demo application in your browser on 
`<http://localhost:6543>`_. A LDF-server is also included
in the demo, which is accessible on `<http://localhost:3000>`_.

.. code::

   $ sudo docker pull atramhasis/demo
   $ sudo docker run -p 6543:6543 -p 3000:3000 atramhasis/demo

Alternatively, you can run a specific version of Atramhasis 
(starting from atramhasis 0.6.4):

.. code::

   $ sudo docker pull atramhasis/demo:0.6.4
   $ sudo docker run -p 6543:6543 -p 3000:3000 atramhasis/demo:0.6.4

While this is a fast and easy way to get a first impression of 
Atramhasis, please be aware  that any edits you make when running the 
image, will be discarded when you stop the Docker container. If you want 
to test the application over a longer period of time, this is probably not
what you're looking for. If you need persistence, but still want to use
Docker, you can customise the 
`Dockerfile <https://github.com/OnroerendErfgoed/atramhasis-demo-docker/>`_
to suit your needs.

Running a demo site on Heroku
=============================

.. warning::

    This older documentation, written for a previous version, and probably
    doesn't work anymore.

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
    
   $ python -m venv atramhasis_heroku
   $ . atramhasis_heroku/bin/activate
   # Make sure pip and setuptools are up to date
   $ pip install --upgrade pip setuptools
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
