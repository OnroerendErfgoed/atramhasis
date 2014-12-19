from pyramid.config import Configurator
from atramhasis.renderers import json_renderer_verbose
from .models import Base


def includeme(config):
    """this function adds some configuration for the application"""
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('csv', 'atramhasis.renderers.CSVRenderer')
    config.add_renderer('skosrenderer_verbose', json_renderer_verbose)
    # Rewrite urls with trailing slash
    config.include('pyramid_rewrite')
    config.add_rewrite_rule(r'/(?P<path>.*)/', r'/%(path)s')
    config.add_route('home', '/')
    config.add_route('conceptschemes', pattern='/conceptschemes', accept='text/html', request_method="GET")
    config.add_route('conceptscheme', pattern='/conceptschemes/{scheme_id}', accept='text/html', request_method="GET")
    config.add_route('concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='text/html',
                     request_method="GET")
    config.add_route('search_result', pattern='/conceptschemes/{scheme_id}/c', accept='text/html')
    config.add_route('scheme_root', pattern='/conceptschemes/{scheme_id}/c/', accept='text/html')
    config.add_route('scheme_tree', pattern='/conceptschemes/{scheme_id}/tree', accept='application/json')
    config.add_route('search_result_export', pattern='/conceptschemes/{scheme_id}/c.csv')
    config.add_route('atramhasis.get_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='application/json',
                     request_method="GET")
    config.add_route('atramhasis.add_concept', pattern='/conceptschemes/{scheme_id}/c', accept='application/json',
                     request_method="POST")
    config.add_route('atramhasis.edit_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='application/json',
                     request_method="PUT")
    config.add_route('atramhasis.delete_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='application/json',
                     request_method="DELETE")
    config.add_route('atramhasis.list_languages', pattern='/languages', accept='application/json',
                     request_method="GET")
    config.add_route('atramhasis.get_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="GET")
    config.add_route('atramhasis.edit_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="PUT")
    config.add_route('atramhasis.delete_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="DELETE")
    config.add_route('locale', '/locale')
    config.add_route('labeltypes', '/labeltypes', accept='application/json', request_method="GET")
    config.add_route('notetypes', '/notetypes', accept='application/json', request_method="GET")

    config.add_route('admin', '/admin')
    config.add_route('scheme_tree_invalidate', pattern='/admin/tree/invalidate/{scheme_id}', accept='application/json')
    config.add_route('tree_invalidate', pattern='/admin/tree/invalidate', accept='application/json')
    config.add_route('atramhasis.rdf_export_turtle', pattern='/conceptschemes/{scheme_id}/c.ttl')
    config.add_route('atramhasis.rdf_export', pattern='/conceptschemes/{scheme_id}/c.rdf')
    config.include('pyramid_skosprovider')
    config.scan('pyramid_skosprovider')

    config.scan()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    includeme(config)

    config.add_translation_dirs('atramhasis:locale/')

    config.include('atramhasis:db')

    # if standalone include skos sample data
    test_mode = settings.get('atramhasis.test_mode')
    if not test_mode == 'true':   # pragma: no cover
        config.include('.skos')

    return config.make_wsgi_app()
