===========================
atramhasis scaffold project
===========================

Requirements
------------

* Python 3.9+
* cookiecutter

Usage
-----

#.  Use cookiecutter to generate the scaffold project

    .. code-block:: bash

        $ cookiecutter gh:OnroerendErfgoed/atramhasis --directory cookiecutter

#.  Create a virtual environment and install requirements

    .. code-block:: bash

        # create a new virtual environment for the project, fe python -m venv $HOME/.virtualenvs/atramhasis_scaffold_venv
        # Change directory into your newly created project if not already there.
        # The [dev] optional requirement will install the waitress WSGI server.
        # You are of course free to choose another.
        $ pip install -e .[dev]

#.  Setup database

    .. code-block:: bash

        $ alembic upgrade head

    Optionally, add demo data:

    .. code-block:: bash

        $ initialize_atramhasis_db development.ini

#.  Run server

    .. code-block:: bash

        $ cd <root of repo>
        $ pserve development.ini
