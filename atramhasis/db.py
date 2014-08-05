# -*- coding: utf-8 -*-
'''
Module that sets up SQLAlchemy.
'''
from .models import Base
from skosprovider_sqlalchemy.models import Base as SkosBase

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


def db(request):
    '''
    Generate a database session and register a cleanup handler.

    :param pyramid.request.Request request: The request this db session will
        be tied to.
    :returns: A :class:`sqlalchemy.orm.session.Session`
    '''
    session = request.registry.dbmaker()

    def cleanup(request):
        session.close()
    request.add_finished_callback(cleanup)

    return session


def includeme(config):
    '''
    Set up SQLAlchemy.

    :param pyramid.config.Configurator config: Pyramid configuration.
    '''

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
