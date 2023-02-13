import configparser
from logging.config import fileConfig
from os import path

from alembic import context
from skosprovider_sqlalchemy.models import Base as SkosBase
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.schema import MetaData

from atramhasis.data.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [SkosBase.metadata, Base.metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def load_app_ini(ini_file):
    """Load the settings for the application.ini file."""
    ini = configparser.ConfigParser()
    with open(ini_file) as f:
        ini.read_file(f)
    here = path.abspath(path.dirname(ini_file))
    ini.set("app:main", "here", here)
    return ini


app_ini = config.get_main_option("ini_location")
app_config = load_app_ini(app_ini)
sa_url = app_config.get("app:main", "sqlalchemy.url")
config.set_main_option("sqlalchemy.url", sa_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, render_as_batch=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    metadata = MetaData()
    for md in target_metadata:
        for table in md.tables.values():
            table.tometadata(metadata)

    connection = engine.connect()
    context.configure(
        connection=connection, target_metadata=metadata, render_as_batch=True
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
