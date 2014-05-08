from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config
from skosprovider_sqlalchemy.models import Base as SkosBase

from .models import Base
from .security import Root, groupfinder


def includeme(config):
    """this function adds some configuration for the application"""
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('csv', 'atramhasis.renderers.CSVRenderer')
    config.add_renderer('treejson', 'atramhasis.renderers.json_tree_renderer')
    config.add_route('home', '/')
    config.add_route('concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='text/html')
    config.add_route('search_result', pattern='/conceptschemes/{scheme_id}/c', accept='text/html')
    config.add_route('scheme_root', pattern='/conceptschemes/{scheme_id}/c/', accept='text/html')
    config.add_route('scheme_tree', pattern='/conceptschemes/{scheme_id}/tree', accept='application/json')
    config.add_route('search_result_export', pattern='/conceptschemes/{scheme_id}/c.csv')
    config.add_route('atramhasis.add_concept', pattern='/conceptschemes/{scheme_id}/c', accept='application/json',
                     request_method="POST")
    config.add_route('atramhasis.edit_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='application/json',
                     request_method="PUT")
    config.add_route('atramhasis.delete_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='application/json',
                     request_method="DELETE")
    config.add_route('locale', '/locale')
    config.add_route('admin', '/admin')
    config.include('pyramid_skosprovider')
    config.scan('pyramid_skosprovider')

    config.scan()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.bind = engine
    SkosBase.metadata.bind = engine
    config = Configurator(settings=settings)
    includeme(config)

    config.add_translation_dirs('atramhasis:locale/')

    config.include('atramhasis:db')

    # Set up security
    config.add_route('login', '/auth/login')
    config.add_route('logout', '/auth/logout')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512', debug=True))
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(Root)

    # if standalone include skos sample data
    config.include('.skos')

    return config.make_wsgi_app()
