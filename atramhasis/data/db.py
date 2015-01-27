# -*- coding: utf-8 -*-
'''
Module that sets up SQLAlchemy.
'''
from atramhasis.data.datamanagers import SkosManager, ConceptSchemeManager, LanguagesManager
from .models import Base
from skosprovider_sqlalchemy.models import Base as SkosBase

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


def data_managers(request):
    '''
    Generate a database session and register a cleanup handler.

    :param pyramid.request.Request request: The request this db session will
        be tied to.
    :returns: A :class:`sqlalchemy.orm.session.Session`
    '''
    session = request.registry.dbmaker()
    skos_manager = SkosManager(session)
    conceptscheme_manager = ConceptSchemeManager(session)
    languages_manager = LanguagesManager(session)

    def cleanup(request):
        session.close()
    request.add_finished_callback(cleanup)

    return {'skos_manager': skos_manager, 'conceptscheme_manager': conceptscheme_manager,
            'languages_manager': languages_manager}


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
    config.add_request_method(data_managers, reify=True)
