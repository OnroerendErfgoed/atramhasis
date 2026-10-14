import logging

from pyramid.exceptions import ConfigurationError
from pyramid.request import Request
from pyramid.response import Response
from pyramid.settings import aslist

from atramhasis.data.models import ConceptschemeVisitLog
from atramhasis.data.models import ConceptVisitLog

log = logging.getLogger(__name__)


def parse_origins_setting(settings):
    """
    Parse the `atramhasis.audit.origins` setting into a set of origins.

    A missing or empty value, or a value listing all origins, resolves to all origin
    values. Unknown origins raise a :class:`pyramid.exceptions.ConfigurationError`.
    """
    key = "atramhasis.audit.origins"
    default = set({"HTML", "REST", "RDF", "CSV"})
    origins = set(aslist(settings.get(key) or ""))

    invalid = origins - default
    if invalid:
        raise ConfigurationError(
            f"Invalid origin(s) for setting '{key}': {', '.join(sorted(invalid))}. "
            f"Allowed: {', '.join(sorted(default))}."
        )

    settings[key] = origins or default


def _get_origin(request: Request, response: Response) -> str | None:
    if isinstance(response, Response):
        return _origin_from_response(response)
    else:
        return _origin_from_request(request)


def _origin_from_request(request) -> str | None:
    if ".csv" in request.url:
        return "CSV"
    elif "text/html" in request.accept:
        return "HTML"
    elif "application/json" in request.accept:
        return "REST"
    elif "application/ld+json" in request.accept:
        return "RDF"
    else:
        return None


def _origin_from_response(response) -> str | None:
    if response.content_type == "text/csv":
        return "CSV"
    elif response.content_type == "text/html":
        return "HTML"
    elif response.content_type == "application/json":
        return "REST"
    elif response.content_type in (
        "application/rdf+xml",
        "application/ld+json",
        "text/turtle",
        "application/x-turtle",
    ):
        return "RDF"
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

    Only origins listed in the `atramhasis.audit.origins` setting are logged.
    """

    def advice(parent_object, *args, **kw):
        response = fn(parent_object, *args, **kw)

        request = parent_object.request
        path_params = request.matchdict

        scheme_id = path_params.get("scheme_id")
        if scheme_id is None:
            log.error(
                "Misuse of the audit decorator. "
                "The url must at least contain a {scheme_id} parameter"
            )
            return response

        provider = request.skos_registry.get_provider(scheme_id)
        if not provider or "external" in provider.get_metadata()["subject"]:
            return response

        origins_to_log = request.registry.settings["atramhasis.audit.origins"]
        origin = _get_origin(request, response)
        if origin not in origins_to_log:
            return response

        if "c_id" in path_params:
            visit_log = ConceptVisitLog(
                concept_id=path_params["c_id"],
                conceptscheme_id=scheme_id,
                origin=origin,
            )
        else:
            visit_log = ConceptschemeVisitLog(
                conceptscheme_id=scheme_id,
                origin=origin,
            )
        audit_manager = request.data_managers["audit_manager"]
        audit_manager.save(visit_log)

        return response

    return advice
