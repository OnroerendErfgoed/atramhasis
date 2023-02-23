import logging

from pyramid.response import Response

from atramhasis.data.models import ConceptVisitLog
from atramhasis.data.models import ConceptschemeVisitLog

log = logging.getLogger(__name__)


def _origin_from_request(request):
    if '.csv' in request.url:
        return 'CSV'
    elif 'text/html' in request.accept:
        return 'HTML'
    elif 'application/json' in request.accept:
        return 'REST'
    elif 'application/ld+json' in request.accept:
        return 'RDF'
    else:
        return None


def _origin_from_response(response):
    if response.content_type == 'application/rdf+xml' \
            or response.content_type == 'application/ld+json' \
            or response.content_type == 'text/turtle' \
            or response.content_type == 'application/x-turtle':
        return 'RDF'
    else:
        return None


def audit(fn):
    """
    use this decorator to audit an operation and to log the visit
    external conceptschemes won't be logged

    * CSV routes with .csv extensions accept all mime types,
      the response is not of the `pyramid.response.Response` type,
      the origin is derived from the `pyramid.request.Request.url` extension.
    * RDF routes with .rdf, .ttl extensions accept all mime types,
      the origin is derived form the response content type.
    * REST and HTML the view results are not of the `pyramid.response.Response` type,
      the origin is derived from the accept header.
    """

    def advice(parent_object, *args, **kw):
        request = parent_object.request
        audit_manager = request.data_managers['audit_manager']

        if 'scheme_id' not in request.matchdict.keys():
            log.error('Misuse of the audit decorator. The url must at least contain a {scheme_id} parameter')
            return fn(parent_object, *args, **kw)

        provider = request.skos_registry.get_provider(request.matchdict['scheme_id'])
        if not provider or 'external' in provider.get_metadata()['subject']:
            return fn(parent_object, *args, **kw)
        else:
            if 'c_id' in request.matchdict.keys():
                visit_log = ConceptVisitLog(
                    concept_id=request.matchdict['c_id'],
                    conceptscheme_id=request.matchdict['scheme_id']
                )
            else:
                visit_log = ConceptschemeVisitLog(conceptscheme_id=request.matchdict['scheme_id'])
            response = fn(parent_object, *args, **kw)

            if isinstance(response, Response):
                visit_log.origin = _origin_from_response(response)
            else:
                visit_log.origin = _origin_from_request(request)

            audit_manager.save(visit_log)

        return response

    return advice
