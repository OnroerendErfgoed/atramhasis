# -*- coding: utf-8 -*-
from .models import Base
from skosprovider_sqlalchemy.models import Base as SkosBase

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


def db(request):
    session = request.registry.dbmaker()

    def cleanup(request):
        session.close()
    request.add_finished_callback(cleanup)

    return session


def includeme(config):

    # Setting up SQLAlchemy
    engine = engine_from_config(config.get_settings(), 'sqlalchemy.')
    Base.metadata.bind = engine
    SkosBase.metadata.bind = engine
    session_maker = sessionmaker(
        bind=engine,
        extension=ZopeTransactionExtension()
    )
    config.registry.dbmaker = session_maker
    config.add_request_method(db, reify=True)
