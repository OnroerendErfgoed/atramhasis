"""
Module containing utility functions dealing with RDF used by Atramhasis.

.. versionadded:: 0.6.0
"""

from pyramid.settings import asbool
from rdflib import Graph
from rdflib import DCTERMS
from rdflib import FOAF
from rdflib import Namespace
from rdflib import RDF
from rdflib import SKOS
from rdflib import VOID
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.term import URIRef
from skosprovider_rdf.utils import _add_labels

FORMATS = Namespace('http://www.w3.org/ns/formats/')
SKOS_THES = Namespace('http://purl.org/iso25964/skos-thes#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')


def void_dumper(request, registry):
    """
    Creates a void file with information about all void Datasets in this Atramhasis instance.

    :param request: pyramid.request.Request request
    :param registry: skosprovider.registry.Registry
    """
    providers = [
        x for x in registry.get_providers()
        if not any([not_shown in x.get_metadata()['subject'] for not_shown in ['external']])
    ]
    graph = Graph()
    graph.namespace_manager.bind("void", VOID)
    graph.namespace_manager.bind("dcterms", DCTERMS)
    graph.namespace_manager.bind("foaf", FOAF)
    graph.namespace_manager.bind("skos", SKOS)
    graph.namespace_manager.bind("skos-thes", SKOS_THES)
    graph.namespace_manager.bind("hydra", HYDRA)
    duri = request.route_url('atramhasis.rdf_void_turtle_ext', _anchor='atramhasis')
    dataset = URIRef(duri)
    graph.add((dataset, RDF.type, VOID.Dataset))
    graph.add((dataset, FOAF.homepage, URIRef(request.route_url('home'))))
    graph.add((dataset, VOID.vocabulary, URIRef(DCTERMS)))
    graph.add((dataset, VOID.vocabulary, URIRef(SKOS)))
    graph.add((dataset, VOID.vocabulary, URIRef(SKOS_THES)))
    ldf_enabled = asbool(request.registry.settings.get('atramhasis.ldf.enabled'))
    ldf_baseurl = request.registry.settings.get('atramhasis.ldf.baseurl')
    if ldf_enabled and ldf_baseurl:
        ldfurl = ldf_baseurl + '/composite{?s,p,o}'
        _add_ldf_server(graph, dataset, ldfurl)
    for p in providers:
        _add_provider(graph, p, dataset, request)
    return graph


def _add_provider(graph, provider, dataseturi, request):
    """
    :param rdflib.graph.Graph graph: Graph that will contain the Dataset.
    :param skosprovider.providers.VocabularyProvider provider: Provider to turn into a Dataset.
    :param rdflib.term.URIRef dataseturi: URI of the main dataset this provider will be attached to.
    :param pyramid.request.Request request:
    :rtype: :class:`rdflib.graph.Graph`
    """
    pid = provider.get_vocabulary_id()
    metadataset = provider.get_metadata().get('dataset', {})
    duri = metadataset.get(
        'uri',
        request.route_url('atramhasis.rdf_void_turtle_ext', _anchor=pid)
    )
    pd = URIRef(duri)
    graph.add((pd, RDF.type, VOID.Dataset))
    graph.add((dataseturi, VOID.subset, pd))
    graph.add((pd, DCTERMS.identifier, Literal(pid)))
    graph.add((pd, VOID.rootResource, URIRef(provider.concept_scheme.uri)))
    graph.add((pd, FOAF.homepage, URIRef(request.route_url('conceptscheme', scheme_id=pid))))
    _add_labels(graph, provider.concept_scheme, pd)
    _add_metadataset(graph, pd, metadataset)
    fmap = [
        ('rdf', FORMATS.RDF_XML, 'atramhasis.rdf_full_export_ext'),
        ('ttl', FORMATS.Turtle, 'atramhasis.rdf_full_export_turtle_ext')
    ]
    for f in fmap:
        graph.add((pd, VOID.feature, f[1]))
        dump_url = request.route_url(f[2], scheme_id=pid)
        graph.add((pd, VOID.dataDump, URIRef(dump_url)))

    ldf_enabled = asbool(request.registry.settings.get('atramhasis.ldf.enabled'))
    ldf_baseurl = request.registry.settings.get('atramhasis.ldf.baseurl')
    if ldf_enabled and ldf_baseurl:
        pid = provider.get_vocabulary_id()
        ldfurl = ldf_baseurl + '/' + pid + '{?s,p,o}'
        _add_ldf_server(graph, pd, ldfurl)
    return graph


def _add_metadataset(graph, subject, metadataset):
    """
    :param rdflib.graph.Graph graph: Graph that contains the Dataset.
    :param rdflib.term.URIRef subject: Uri of the Dataset.
    :param dict metadataset: Dictionary with metadata to add to the Dataset.
    :rtype: :class:`rdflib.graph.Graph`
    """
    mapping = {
        'creator': {
            'predicate': DCTERMS.creator,
            'objecttype': URIRef
        },
        'publisher': {
            'predicate': DCTERMS.publisher,
            'objecttype': URIRef
        },
        'contributor': {
            'predicate': DCTERMS.contributor,
            'objecttype': URIRef
        },
        'language': {
            'predicate': DCTERMS.language
        },
        'date': {
            'predicte': DCTERMS.date
        },
        'created': {
            'predicate': DCTERMS.created
        },
        'issued': {
            'predicate': DCTERMS.issued
        },
        'license': {
            'predicate': DCTERMS.license,
            'objecttype': URIRef
        }
    }

    for k, v in mapping.items():
        if k in metadataset:
            if 'objecttype' in v:
                objecttype = v['objecttype']
            else:
                objecttype = Literal
            for ko in metadataset[k]:
                o = objecttype(ko)
                graph.add((subject, v['predicate'], o))
    return graph


def _add_ldf_server(graph, dataseturi, ldfurl):
    """
    :param rdflib.graph.Graph graph: Graph that contains the Dataset.
    :param rdflib.term.URIRef dataseturi: Uri of the Dataset.
    :param str ldfurl: Url pointing to the ldf server.
    :rtype: :class:`rdflib.graph.Graph`
    """
    ldf = BNode()
    graph.add((dataseturi, HYDRA.search, ldf))
    graph.add((ldf, HYDRA.template, Literal(ldfurl)))
    s = BNode()
    graph.add((s, HYDRA.variable, Literal('s')))
    graph.add((s, HYDRA.property, RDF.subject))
    graph.add((ldf, HYDRA.mapping, s))
    p = BNode()
    graph.add((p, HYDRA.variable, Literal('p')))
    graph.add((p, HYDRA.property, RDF.predicate))
    graph.add((ldf, HYDRA.mapping, p))
    o = BNode()
    graph.add((o, HYDRA.variable, Literal('o')))
    graph.add((o, HYDRA.property, RDF.object))
    graph.add((ldf, HYDRA.mapping, o))
    return graph
