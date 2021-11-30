# -*- coding: utf-8 -*-
import os

from pyramid.renderers import render
from pyramid.response import Response, FileResponse
from pyramid.view import view_defaults, view_config
from pyramid_skosprovider.views import ProviderView
from skosprovider_rdf import utils

from atramhasis.errors import (
    SkosRegistryNotFoundException,
    ConceptSchemeNotFoundException,
    ConceptNotFoundException
)
from atramhasis.audit import audit

from atramhasis.rdf import void_dumper

@view_defaults()
class AtramhasisVoid(object):

    def __init__(self, request):
        self.request = request
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()   # pragma: no cover

    @view_config(route_name='atramhasis.rdf_void_turtle_ext')
    def rdf_void_turtle(self):
        graph = void_dumper(self.request, self.skos_registry)
        response = Response(content_type='text/turtle')
        response.body = graph.serialize(format='turtle')
        response.content_disposition = 'attachment; filename="void.ttl"'
        return response


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
        dump_location = self.request.registry.settings['atramhasis.dump_location']
        filename = os.path.join(dump_location, '%s-full.rdf' % self.scheme_id)
        return FileResponse(
            filename,
            request=self.request,
            content_type='application/rdf+xml',
            cache_max_age=86400
        )

    @audit
    @view_config(route_name='atramhasis.rdf_full_export_turtle')
    @view_config(route_name='atramhasis.rdf_full_export_turtle_x')
    @view_config(route_name='atramhasis.rdf_full_export_turtle_ext')
    def rdf_full_export_turtle(self):
        dump_location = self.request.registry.settings['atramhasis.dump_location']
        filename = os.path.join(dump_location, '%s-full.ttl' % self.scheme_id)
        return FileResponse(
            filename,
            request=self.request,
            content_type='text/turtle',
            cache_max_age=86400
        )

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

    @audit
    @view_config(route_name='atramhasis.rdf_conceptscheme_jsonld', permission='view')
    @view_config(route_name='atramhasis.rdf_conceptscheme_jsonld_ext', permission='view')
    def get_conceptscheme_jsonld(self):
        conceptscheme = ProviderView(self.request).get_conceptscheme_jsonld()
        response = Response(content_type='application/ld+json')
        response.text = render('skosjsonld', conceptscheme, self.request)
        response.content_disposition = 'attachment; filename="%s.jsonld"' % (str(self.scheme_id),)
        return response

    @audit
    @view_config(route_name='atramhasis.rdf_individual_jsonld', permission='view')
    @view_config(route_name='atramhasis.rdf_individual_jsonld_ext', permission='view')
    def get_concept(self):
        concept = ProviderView(self.request).get_concept()
        response = Response(content_type='application/ld+json')
        response.text = render('skosjsonld', concept, self.request)
        response.content_disposition = 'attachment; filename="%s.jsonld"' % (str(self.c_id),)
        return response
