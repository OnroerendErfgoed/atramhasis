import logging
import os

from pyramid.config import Configurator
from pyramid.config import PHASE3_CONFIG
from pyramid.interfaces import ISessionFactory
from pyramid.session import SignedCookieSessionFactory
from pyramid.settings import aslist

from atramhasis.renderers import json_renderer_verbose

LOG = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    "cache.tree.backend": "dogpile.cache.memory",
    "cache.tree.arguments.cache_size": "5000",
    "cache.tree.expiration_time": "7000",
    "cache.list.backend": "dogpile.cache.memory",
    "cache.list.arguments.cache_size": "5000",
    "cache.list.expiration_time": "7000",
    "jinja2.extensions": "jinja2.ext.do",
    "jinja2.filters": "label_sort = atramhasis.utils.label_sort",
    "dojo.mode": "dist",
    "layout.focus_conceptschemes": [],
    "skosprovider.skosregistry_factory": "atramhasis.skos.create_registry",
    "skosprovider.skosregistry_location": "request",
}


def includeme(config):
    """this function adds some configuration for the application"""
    settings = config.registry.settings
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value
    configure_session(config)
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('csv', 'atramhasis.renderers.CSVRenderer')
    config.add_renderer('skosrenderer_verbose', json_renderer_verbose)
    # Rewrite urls with trailing slash
    config.include('pyramid_rewrite')
    config.include("pyramid_openapi3")
    config.include('atramhasis.routes')
    config.include('pyramid_skosprovider')
    config.include('atramhasis.cache')
    config.scan('pyramid_skosprovider')

    config.add_translation_dirs('atramhasis:locale/')

    config.scan()


def configure_session(config):
    """
    Configure pyramid's session factory.

    People can configure their own session factory, but if no factory is registered
    atramhasis will try configuring its own.
    """

    def check_session_factory_set():
        session_factory = config.registry.queryUtility(ISessionFactory)
        if session_factory:
            return

        settings = config.registry.settings
        if 'atramhasis.session_factory.secret' not in settings:
            msg = (
                'No session factory is configured, and '
                'atramhasis.session_factory.secret setting is missing.'
            )
            raise ValueError(msg)

        LOG.info('Using default SignedCookieSessionFactory.')
        default_session_factory = SignedCookieSessionFactory(
            settings['atramhasis.session_factory.secret']
        )
        config.registry.registerUtility(default_session_factory, ISessionFactory)

    config.action(
        'check_session_factory_set', check_session_factory_set, order=PHASE3_CONFIG + 1
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['layout.focus_conceptschemes'] = aslist(settings['layout.focus_conceptschemes'], flatten=False)

    dump_location = settings['atramhasis.dump_location']
    if not os.path.exists(dump_location):
        os.makedirs(dump_location)

    config = Configurator(settings=settings)

    return load_app(config)


def load_app(config):
    includeme(config)

    config.include('atramhasis.data:db')

    return config.make_wsgi_app()
