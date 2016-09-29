# -*- coding: utf-8 -*-
"""
Routes for the Atramhasis views.

.. versionadded:: 0.4.4
"""


def includeme(config):
    """
    Setup the routing for Atramhasis.

    :param pyramid.config.Configurator config: The application config.
    """

    config.add_rewrite_rule(r'/(?P<path>.*)/', r'/%(path)s')
    config.add_route('home', '/')

    config.add_route('atramhasis.rdf_void_turtle_ext', pattern='/void.ttl', accept='text/turtle')
    config.add_route('atramhasis.rdf_full_export_ext', pattern='/conceptschemes/{scheme_id}/c.rdf')
    config.add_route('atramhasis.rdf_full_export_turtle_ext', pattern='/conceptschemes/{scheme_id}/c.ttl')
    config.add_route('atramhasis.rdf_conceptscheme_export_ext', pattern='/conceptschemes/{scheme_id}.rdf')
    config.add_route('atramhasis.rdf_conceptscheme_export_turtle_ext', pattern='/conceptschemes/{scheme_id}.ttl')
    config.add_route('atramhasis.rdf_individual_export_ext', pattern='/conceptschemes/{scheme_id}/c/{c_id}.rdf')
    config.add_route('atramhasis.rdf_individual_export_turtle_ext', pattern='/conceptschemes/{scheme_id}/c/{c_id}.ttl')

    config.add_route('conceptschemes', pattern='/conceptschemes', accept='text/html', request_method="GET")
    config.add_route('conceptscheme', pattern='/conceptschemes/{scheme_id}', accept='text/html', request_method="GET")
    config.add_route('concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}', accept='text/html',
                     request_method="GET")
    config.add_route('search_result', pattern='/conceptschemes/{scheme_id}/c', accept='text/html')
    config.add_route('scheme_root', pattern='/conceptschemes/{scheme_id}/c/', accept='text/html')
    config.add_route('scheme_tree', pattern='/conceptschemes/{scheme_id}/tree', accept='application/json')
    config.add_route('search_result_export', pattern='/conceptschemes/{scheme_id}/c.csv')
    config.add_route('atramhasis.edit_conceptscheme', pattern='/conceptschemes/{scheme_id}',
                     accept='application/json', request_method='PUT')
    config.add_route('atramhasis.get_conceptscheme', pattern='/conceptschemes/{scheme_id}', accept='application/json')
    config.add_route('atramhasis.get_conceptschemes', pattern='/conceptschemes', accept='application/json')
    config.add_route('atramhasis.get_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='application/json', request_method="GET")
    config.add_route('atramhasis.add_concept', pattern='/conceptschemes/{scheme_id}/c', accept='application/json',
                     request_method="POST")
    config.add_route('atramhasis.edit_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='application/json', request_method="PUT")
    config.add_route('atramhasis.delete_concept', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='application/json', request_method="DELETE")
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

    config.add_route('atramhasis.rdf_full_export_turtle', pattern='/conceptschemes/{scheme_id}/c', accept='text/turtle')
    config.add_route('atramhasis.rdf_full_export_turtle_x', pattern='/conceptschemes/{scheme_id}/c',
                     accept='application/x-turtle')
    config.add_route('atramhasis.rdf_full_export', pattern='/conceptschemes/{scheme_id}/c',
                     accept='application/rdf+xml')
    config.add_route('atramhasis.rdf_conceptscheme_export', pattern='/conceptschemes/{scheme_id}',
                     accept='application/rdf+xml')
    config.add_route('atramhasis.rdf_conceptscheme_export_turtle', pattern='/conceptschemes/{scheme_id}',
                     accept='text/turtle')
    config.add_route('atramhasis.rdf_conceptscheme_export_turtle_x', pattern='/conceptschemes/{scheme_id}',
                     accept='application/x-turtle')
    config.add_route('atramhasis.rdf_individual_export', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='application/rdf+xml')
    config.add_route('atramhasis.rdf_individual_export_turtle', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='text/turtle')
    config.add_route('atramhasis.rdf_individual_export_turtle_x', pattern='/conceptschemes/{scheme_id}/c/{c_id}',
                     accept='application/x-turtle')
