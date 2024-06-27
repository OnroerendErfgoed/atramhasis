=======================
atramhasis demo project
=======================

Requirements
------------

*   Python 3.9+
*   npm

Usage
-----

#. Use cookiecutter to generate the scaffold project

.. code-block:: bash

    $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory cookiecutters/scaffold

#.  Create a virtual environment and install requirements

    .. code-block:: bash

        # create a new virtual environment for the project, fe python -m venv $HOME/.virtualenvs/atramhasis_demo_venv
        # Change directory into your newly created project if not already there.
        $ pip install -r requirements-dev.txt
        $ pip install -e .

#.  Setup database

    .. code-block:: bash

        $ alembic upgrade head

#.  Run server

    .. code-block:: bash

        $ cd <root of repo>
        $ pserve development.ini
