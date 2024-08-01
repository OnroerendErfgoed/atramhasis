"""
Routes for the Atramhasis views.

.. versionadded:: 0.4.4
"""
import os


def includeme(config):
    """
    Setup the routing for Atramhasis.

    :param pyramid.config.Configurator config: The application config.
    """

    config.add_rewrite_rule(r'/(?P<path>.*)/', r'/%(path)s')
    config.add_route('home', '/')

    # Configure pyramid_openapi3 integration
    config.pyramid_openapi3_spec(
        os.path.join(os.path.dirname(__file__), "openapi.yaml"),
        route="/api_doc/openapi.yaml",
    )
    config.pyramid_openapi3_add_explorer(route="/api_doc")

    config.add_static_view('sitemaps', 'static/_sitemaps/', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route("sitemap", "/sitemap_index.xml")

    # APIs with extensions instead of accept headers
    config.add_route('atramhasis.rdf_void_turtle_ext', pattern='/void.ttl', accept='text/turtle')
    # The routes below extend the existing skosprovider routes with extensions
    config.add_route('skosprovider.conceptscheme.cs.rdf', pattern='/conceptschemes/{scheme_id}/c.rdf')
    config.add_route('skosprovider.conceptscheme.cs.ttl', pattern='/conceptschemes/{scheme_id}/c.ttl')
    config.add_route('skosprovider.conceptscheme.rdf', pattern='/conceptschemes/{scheme_id}.rdf')
    config.add_route('skosprovider.conceptscheme.ttl', pattern='/conceptschemes/{scheme_id}.ttl')
    config.add_route('skosprovider.conceptscheme.csv', pattern='/conceptschemes/{scheme_id}/c.csv')
    config.add_route('skosprovider.c.rdf', pattern='/conceptschemes/{scheme_id}/c/{c_id:.*}.rdf')
    config.add_route('skosprovider.c.ttl', pattern='/conceptschemes/{scheme_id}/c/{c_id:.*}.ttl')

    # tree
    config.add_route('scheme_tree_html', pattern='/conceptschemes/{scheme_id}/tree', accept='text/html')
    config.add_route('scheme_tree', pattern='/conceptschemes/{scheme_id}/tree', accept='application/json')

    # language
    config.add_route('atramhasis.list_languages', pattern='/languages', accept='application/json',
                     request_method="GET")
    config.add_route('atramhasis.get_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="GET")
    config.add_route('atramhasis.edit_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="PUT")
    config.add_route('atramhasis.delete_language', pattern='/languages/{l_id}', accept='application/json',
                     request_method="DELETE")
    config.add_route('locale', '/locale')

    # admin
    config.add_route('admin', '/admin')
    config.add_route('scheme_tree_invalidate', pattern='/admin/tree/invalidate/{scheme_id}', accept='application/json')
    config.add_route('tree_invalidate', pattern='/admin/tree/invalidate', accept='application/json')

    # providers
    config.add_route('atramhasis.providers', pattern='/providers')
    config.add_route('atramhasis.provider', pattern='/providers/{id}')

    # other
    config.add_route('labeltypes', '/labeltypes', accept='application/json', request_method="GET")
    config.add_route('notetypes', '/notetypes', accept='application/json', request_method="GET")
