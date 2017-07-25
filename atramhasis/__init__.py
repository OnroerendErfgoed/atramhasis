import os

from pyramid.config import Configurator
from pyramid.settings import aslist

from atramhasis.renderers import json_renderer_verbose


def includeme(config):
    """this function adds some configuration for the application"""
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('csv', 'atramhasis.renderers.CSVRenderer')
    config.add_renderer('skosrenderer_verbose', json_renderer_verbose)
    # Rewrite urls with trailing slash
    config.include('pyramid_rewrite')
    config.include('atramhasis.routes')
    config.include('pyramid_skosprovider')
    config.include('atramhasis.cache')
    config.scan('pyramid_skosprovider')

    config.scan()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['layout.focus_conceptschemes'] = aslist(settings['layout.focus_conceptschemes'], flatten=False)

    dump_location = settings['atramhasis.dump_location']
    if not os.path.exists(dump_location):
        os.makedirs(dump_location)

    config = Configurator(settings=settings)

    from pyramid.session import SignedCookieSessionFactory
    atramhasis_session_factory = SignedCookieSessionFactory(settings['atramhasis.session_factory.secret'])
    config.set_session_factory(atramhasis_session_factory)

    includeme(config)

    config.add_translation_dirs('atramhasis:locale/')

    config.include('atramhasis.data:db')

    # if standalone include skos sample data
    test_mode = settings.get('atramhasis.test_mode')
    if not test_mode == 'true':  # pragma: no cover
        config.include('.skos')

    return config.make_wsgi_app()
