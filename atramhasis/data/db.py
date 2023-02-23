"""
Module that sets up the datamanagers and the database connections.
"""
from skosprovider_sqlalchemy.models import Base as SkosBase
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register

from atramhasis.data.datamanagers import AuditManager
from atramhasis.data.datamanagers import ConceptSchemeManager
from atramhasis.data.datamanagers import LanguagesManager
from atramhasis.data.datamanagers import SkosManager
from .models import Base


def data_managers(request):
    """
    Generate a datamanager with a database session and register a cleanup handler.

    :param pyramid.request.Request request: The request this db session will
        be tied to.
    :returns: A dictionary containing different
        :class:`datamanagers <atramhasis.data.datamanagers.DataManager>`.
    """
    session = request.db
    skos_manager = SkosManager(session)
    conceptscheme_manager = ConceptSchemeManager(session)
    languages_manager = LanguagesManager(session)
    audit_manager = AuditManager(session)

    return {'skos_manager': skos_manager, 'conceptscheme_manager': conceptscheme_manager,
            'languages_manager': languages_manager, 'audit_manager': audit_manager}


def db(request):
    session = request.registry.dbmaker()

    def cleanup(_):
        session.close()
    request.add_finished_callback(cleanup)
    return session


def includeme(config):
    """
    Set up SQLAlchemy.

    :param pyramid.config.Configurator config: Pyramid configuration.
    """

    # Setting up SQLAlchemy
    engine = engine_from_config(config.get_settings(), 'sqlalchemy.')
    Base.metadata.bind = engine
    SkosBase.metadata.bind = engine
    config.registry.dbmaker = sessionmaker(bind=engine)
    register(config.registry.dbmaker)
    config.add_request_method(data_managers, reify=True)
    config.add_request_method(db, reify=True)
