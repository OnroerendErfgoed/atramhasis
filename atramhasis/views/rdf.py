from pyramid.response import Response
from pyramid.view import view_defaults, view_config
from skosprovider_rdf import utils

from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException


@view_defaults()
class AtramhasisRDF(object):

    def __init__(self, request):
        self.request = request
        self.db = request.db
        self.scheme_id = self.request.matchdict['scheme_id']

        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()   # pragma: no cover
        self.provider = self.skos_registry.get_provider(self.scheme_id)
        if not self.provider:
            raise ConceptSchemeNotFoundException(self.scheme_id)   # pragma: no cover

    @view_config(route_name='atramhasis.rdf_export')
    def rdf_export(self):
        graph = utils.rdf_dumper(self.provider)
        response = Response(content_type='application/rdf+xml')
        response.body = graph.serialize(format='xml')
        response.content_disposition = 'attachment; filename="skos.xml"'
        return response

    @view_config(route_name='atramhasis.rdf_export_turtle', accept='text/turtle')
    def rdf_export_turtle(self):
        graph = utils.rdf_dumper(self.provider)
        response = Response(content_type='text/turtle')
        response.body = graph.serialize(format='turtle')
        response.content_disposition = 'attachment; filename="skos.ttl"'
        return response