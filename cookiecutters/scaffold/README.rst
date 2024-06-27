==================
atramhasis project
==================

Requirements
------------

*   Python 3.9+
*   npm

Usage
-----

#.  Use cookiecutter to generate an atramhasis project

    .. code-block:: bash

        $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory cookiecutters/scaffold

#.  Create a virtual environment and install requirements

    .. code-block:: bash

        # create a new virtual environment for the project, fe python -m venv $HOME/.virtualenvs/atramhasis_demo_venv
        # Change directory into your newly created project if not already there.
        # The [dev] optional requirement will install the waitress WSGI server.
        # You are of course free to choose another.
        $ pip install -e .[dev]

#.  Setup database

    .. code-block:: bash

        $ alembic upgrade head

#.  Run server

    .. code-block:: bash

        $ cd <root of repo>
        $ pserve development.ini
