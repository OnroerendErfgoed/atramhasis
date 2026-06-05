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

    # set VENV_PATH to the desired location for your new virtual environment
    $ VENV_PATH=$HOME/Envs
    # create a new virtual environment for the project
    $ python -m venv $VENV_PATH/my_atramhasis
    $ . $VENV_PATH/my_atramhasis/bin/activate
    # Make sure pip and pip-tools are up to date
    $ pip install --upgrade pip
    $ pip install --upgrade cookiecutter

2.  Use cookiecutter to generate an demo project

.. code-block:: bash

    $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory cookiecutters/demo

Running this command will ask a few questions. Just accept the default answers,
unless you want to give your project a different name. After the
cookiecutter command, there should be a directory with the name of your
project (default: atramhasis_demo). Now enter this directory to start updating your virtual environment.


3.  Install requirements

.. code-block:: bash

    $ cd <root of newly from scaffold created project>
    # Install the new project in editable mode via argument -e
    $ pip install -e ."[dev]"


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

6.  Run server

.. code-block:: bash

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
