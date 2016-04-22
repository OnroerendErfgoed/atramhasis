from pyramid.response import Response
from pyramid.view import view_defaults, view_config
from skosprovider_rdf import utils

from atramhasis.errors import (
    SkosRegistryNotFoundException,
    ConceptSchemeNotFoundException,
    ConceptNotFoundException
)
from atramhasis.audit import audit


@view_defaults()
class AtramhasisRDF(object):

    def __init__(self, request):
        self.request = request
        self.scheme_id = self.request.matchdict['scheme_id']
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()   # pragma: no cover
        self.provider = self.skos_registry.get_provider(self.scheme_id)
        if not self.provider:
            raise ConceptSchemeNotFoundException(self.scheme_id)   # pragma: no cover
        if 'c_id' in self.request.matchdict.keys():
            self.c_id = self.request.matchdict['c_id']
            if not self.c_id.isdigit() or not self.provider.get_by_id(int(self.c_id)):
                raise ConceptNotFoundException(self.c_id)

    @audit
    @view_config(route_name='atramhasis.rdf_full_export')
    @view_config(route_name='atramhasis.rdf_full_export_ext')
    def rdf_full_export(self):
        graph = utils.rdf_dumper(self.provider)
        response = Response(content_type='application/rdf+xml')
        response.body = graph.serialize(format='xml')
        response.content_disposition = 'attachment; filename="%s-full.rdf"' % (str(self.scheme_id),)
        return response

    @audit
    @view_config(route_name='atramhasis.rdf_full_export_turtle')
    @view_config(route_name='atramhasis.rdf_full_export_turtle_x')
    @view_config(route_name='atramhasis.rdf_full_export_turtle_ext')
    def rdf_full_export_turtle(self):
        graph = utils.rdf_dumper(self.provider)
        response = Response(content_type='text/turtle')
        response.body = graph.serialize(format='turtle')
        response.content_disposition = 'attachment; filename="%s-full.ttl"' % (str(self.scheme_id),)
        return response

    @audit
    @view_config(route_name='atramhasis.rdf_conceptscheme_export')
    @view_config(route_name='atramhasis.rdf_conceptscheme_export_ext')
    def rdf_conceptscheme_export(self):
        graph = utils.rdf_conceptscheme_dumper(self.provider)
        response = Response(content_type='application/rdf+xml')
        response.body = graph.serialize(format='xml')
        response.content_disposition = 'attachment; filename="%s.rdf"' % (str(self.scheme_id),)
        return response

    @view_config(route_name='atramhasis.rdf_conceptscheme_export_turtle')
    @view_config(route_name='atramhasis.rdf_conceptscheme_export_turtle_x')
    @view_config(route_name='atramhasis.rdf_conceptscheme_export_turtle_ext')
    def rdf_conceptscheme_export_turtle(self):
        graph = utils.rdf_conceptscheme_dumper(self.provider)
        response = Response(content_type='text/turtle')
        response.body = graph.serialize(format='turtle')
        response.content_disposition = 'attachment; filename="%s.ttl"' % (str(self.scheme_id),)
        return response

    @audit
    @view_config(route_name='atramhasis.rdf_individual_export')
    @view_config(route_name='atramhasis.rdf_individual_export_ext')
    def rdf_individual_export(self):
        graph = utils.rdf_c_dumper(self.provider, self.c_id)
        response = Response(content_type='application/rdf+xml')
        response.body = graph.serialize(format='xml')
        response.content_disposition = 'attachment; filename="%s.rdf"' % (str(self.c_id),)
        return response

    @audit
    @view_config(route_name='atramhasis.rdf_individual_export_turtle')
    @view_config(route_name='atramhasis.rdf_individual_export_turtle_x')
    @view_config(route_name='atramhasis.rdf_individual_export_turtle_ext')
    def rdf_individual_export_turtle(self):
        graph = utils.rdf_c_dumper(self.provider, self.c_id)
        response = Response(content_type='text/turtle')
        response.body = graph.serialize(format='turtle')
        response.content_disposition = 'attachment; filename="%s.ttl"' % (str(self.c_id),)
        return response
