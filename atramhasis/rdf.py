# -*- coding: utf-8 -*-
"""
Module containing utility functions dealing with RDF used by Atramhasis.

.. versionadded:: 0.6.0
"""

import logging

log = logging.getLogger(__name__)

from pyramid.settings import asbool

from rdflib import Graph
from rdflib.namespace import RDF, VOID, DCTERMS, FOAF, SKOS
from rdflib.namespace import Namespace
from rdflib.term import URIRef, BNode, Literal

from skosprovider_rdf.utils import extract_language, _add_lang_to_html


FORMATS = Namespace('http://www.w3.org/ns/formats/')
SKOS_THES = Namespace('http://purl.org/iso25964/skos-thes#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
CC = Namespace('https://creativecommons.org/ns#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')


def _init_metadata_graph():
    '''
    Initialises the Graph to add VOID or DCAT metadata to.

    :rtype: :class:`rdflib.graph.Graph`
    '''
    graph = Graph()
    graph.namespace_manager.bind("void", VOID)
    graph.namespace_manager.bind("dcat", DCAT)
    graph.namespace_manager.bind("dcterms", DCTERMS)
    graph.namespace_manager.bind("foaf", FOAF)
    graph.namespace_manager.bind("skos", SKOS)
    graph.namespace_manager.bind("skos-thes", SKOS_THES)
    graph.namespace_manager.bind("hydra", HYDRA)
    graph.namespace_manager.bind("cc", CC)
    graph.namespace_manager.bind("vcard", VCARD)
    return graph


def void_dumper(request, registry):
    '''
    Creates a void file with information about all void Datasets in this Atramhasis instance.

    :param pyramid.request.Request request:
    :param skosprovider.registry.Registry:
    '''
    providers = [
        x for x in registry.get_providers()
        if not any([not_shown in x.get_metadata()['subject'] for not_shown in ['external']])
    ]
    graph = _init_metadata_graph()
    voiddataset = URIRef(
        request.route_url('atramhasis.rdf_void_turtle_ext', _anchor='atramhasis')
    )
    dcatcatalog = URIRef(
        request.route_url('atramhasis.rdf_dcat')
    )
    graph.add((voiddataset, RDF.type, VOID.Dataset))
    graph.add((voiddataset, FOAF.homepage, URIRef(request.route_url('home'))))
    graph.add((voiddataset, VOID.vocabulary, URIRef(DCTERMS)))
    graph.add((voiddataset, VOID.vocabulary, URIRef(SKOS)))
    graph.add((voiddataset, VOID.vocabulary, URIRef(SKOS_THES)))
    ldf_enabled = asbool(request.registry.settings.get(
        'atramhasis.ldf.enabled',
        None
    ))
    ldf_baseurl = request.registry.settings.get(
        'atramhasis.ldf.baseurl',
        None
    )
    if ldf_enabled and ldf_baseurl:
        ldfurl = ldf_baseurl + '/composite{?s,p,o}'
        _add_ldf_server(graph, voiddataset, ldfurl)
    for p in providers:
        _add_provider(graph, p, voiddataset, dcatcatalog, request)
    return graph


def dcat_dumper(request, registry):
    '''
    Creates a void file with information about all dcat Datasets in this Atramhasis instance.

    :param pyramid.request.Request request:
    :param skosprovider.registry.Registry:
    '''
    providers = [
        x for x in registry.get_providers()
        if not any([not_shown in x.get_metadata()['subject'] for not_shown in ['external']])
    ]
    graph = _init_metadata_graph()
    voiddataset = URIRef(
        request.route_url('atramhasis.rdf_void_turtle_ext', _anchor='atramhasis')
    )
    catalogmetadataset = registry.get_metadata().get('catalog', {})
    cataloguri = catalogmetadataset.get(
        'uri',
        request.route_url('atramhasis.rdf_dcat')
    )
    dcatcatalog = URIRef(cataloguri)
    graph.add((dcatcatalog, RDF.type, DCAT.Catalog))
    graph.add((dcatcatalog, FOAF.homepage, URIRef(request.route_url('home'))))

    _add_metadata(graph, dcatcatalog, catalogmetadataset)
    ldf_enabled = asbool(request.registry.settings.get(
        'atramhasis.ldf.enabled',
        None
    ))
    ldf_baseurl = request.registry.settings.get(
        'atramhasis.ldf.baseurl',
        None
    )
    if ldf_enabled and ldf_baseurl:
        compositedataset = URIRef(
            request.route_url('atramhasis.rdf_dcat', _anchor='composite')
        )
        graph.add((compositedataset, RDF.type, VOID.Dataset))
        ldfurl = ldf_baseurl + '/composite{?s,p,o}'
        _add_ldf_server(graph, compositedataset, ldfurl)
    for p in providers:
        _add_provider(graph, p, voiddataset, dcatcatalog, request)
    return graph


def _add_provider(graph, provider, dataseturi, cataloguri, request):
    '''
    Add a VOID or DCAT dataset to the Graph.

    :param rdflib.graph.Graph graph: Graph that will contain the Dataset.
    :param skosprovider.providers.VocabularyProvider provider: Provider to turn into a Dataset.
    :param rdflib.term.URIRef URIRef: URI of the main dataset this provider will be attached to.
    :param pyramid.request.Request request:
    :rtype: :class:`rdflib.graph.Graph`
    '''
    pid = provider.get_vocabulary_id()
    metadataset = provider.get_metadata().get('dataset', {})
    duri = metadataset.get(
        'uri',
        request.route_url('atramhasis.rdf_void_turtle_ext', _anchor=pid)
    )
    pd = URIRef(duri)
    graph.add((pd, RDF.type, VOID.Dataset))
    graph.add((pd, RDF.type, DCAT.Dataset))
    graph.add((dataseturi, VOID.subset, pd))
    graph.add((cataloguri, DCAT.dataset, pd))
    graph.add((pd, DCTERMS.identifier, Literal(pid)))
    graph.add((pd, VOID.rootResource, URIRef(provider.concept_scheme.uri)))
    cs_url = request.route_url('conceptscheme', scheme_id=pid)
    graph.add((pd, FOAF.homepage, URIRef(cs_url)))
    graph.add((pd, DCAT.landingPage, URIRef(cs_url)))
    graph.add((pd, VOID.vocabulary, URIRef(DCTERMS)))
    graph.add((pd, VOID.vocabulary, URIRef(SKOS)))
    graph.add((pd, VOID.vocabulary, URIRef(SKOS_THES)))
    _add_dataset_labels(graph, pd, provider.concept_scheme)
    _add_dataset_description(graph, pd, provider.concept_scheme)
    _add_metadata(graph, pd, metadataset)
    fmap = [
        ('rdf', FORMATS.RDF_XML, 'atramhasis.rdf_full_export_ext', 'application/rdf+xml'),
        ('ttl', FORMATS.Turtle, 'atramhasis.rdf_full_export_turtle_ext', 'text/turtle')
    ]
    for f in fmap:
        dump_url = request.route_url(f[2], scheme_id=pid)
        graph.add((pd, VOID.feature, f[1]))
        graph.add((pd, VOID.dataDump, URIRef(dump_url)))

        dist = URIRef(dump_url)
        graph.add((dist, RDF.type, DCAT.Distribution))
        graph.add((dist, DCAT.accessURL, URIRef(cs_url)))
        graph.add((dist, DCAT.downloadURL, URIRef(dump_url)))
        graph.add((dist, DCAT.mediaType, Literal(f[3])))
        _add_dataset_labels(graph, dist, provider.concept_scheme)
        _add_dataset_description(graph, dist, provider.concept_scheme)
        _add_metadata(graph, dist, metadataset)
        graph.add((pd, DCAT.distribution, dist))

    ldf_enabled = asbool(request.registry.settings.get(
        'atramhasis.ldf.enabled',
        None
    ))
    ldf_baseurl = request.registry.settings.get(
        'atramhasis.ldf.baseurl',
        None
    )
    if ldf_enabled and ldf_baseurl:
        pid = provider.get_vocabulary_id()
        ldfurl = ldf_baseurl + '/' + pid + '{?s,p,o}'
        _add_ldf_server(graph, pd, ldfurl)
    return graph

def _add_metadata(graph, subject, metadata):
    '''
    :param rdflib.graph.Graph graph: Graph that contains the subject.
    :param rdflib.term.URIRef subject: Uri of the Resource that will be metadated.
    :param dict metadata: Dictionary with metadata to add to the Resource.
    :rtype: :class:`rdflib.graph.Graph`
    '''
    mapping = {
        'creator': {
            'predicate': DCTERMS.creator,
            'objecttype': 'agent'
        },
        'publisher': {
            'predicate': DCTERMS.publisher,
            'objecttype': 'agent'
        },
        'contributor': {
            'predicate': DCTERMS.contributor,
            'objecttype': 'agent'
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
            'objecttype': 'license'
        },
        'contactPoint': {
            'predicate': DCAT.contactPoint,
            'objecttype': 'vcard'
        }
    }

    for k, v in mapping.items():
        if k in metadata:
            if 'objecttype' in v:
                objecttype = v['objecttype']
            else:
                objecttype = Literal
            for ko in metadata[k]:
                if objecttype == 'agent':
                    _add_agent(graph, subject, v['predicate'], ko)
                elif objecttype == 'license':
                    _add_license(graph, subject, v['predicate'], ko)
                elif objecttype == 'vcard':
                    _add_vcard(graph, subject, v['predicate'], ko)
                else:
                    o = objecttype(ko)
                    graph.add((subject, v['predicate'], o))
    return graph


def _add_vcard(graph, subject, predicate, vcard):
    vcard['type'] = vcard.get('type', [])
    vcard['type'].append(VCARD.Kind)
    mapping = {
        'fn': {
            'predicate': VCARD.fn
        },
        'type': {
            'predicate': RDF.type,
            'objecttype': URIRef
        },
        'hasEmail': {
            'predicate': VCARD.hasEmail,
            'objecttype': 'mapping',
            'mapper': _add_email
        },
        'hasTelephone': {
            'predicate': VCARD.hasTelephone,
            'objecttype': 'mapping',
            'mapper': _add_tel
        },
    }
    return _gen_mapping(graph, subject, predicate, vcard, mapping)


def _add_email(graph, subject, predicate, email):
    email['type'] = email.get('type', [])
    email['type'].append(VCARD.Email)
    mapping = {
        'hasValue': {
            'predicate': VCARD.hasValue,
            'objecttype': URIRef
        },
        'type': {
            'predicate': RDF.type,
            'objecttype': URIRef
        },
    }
    return _gen_mapping(graph, subject, predicate, email, mapping)


def _add_tel(graph, subject, predicate, tel):
    tel['type'] = tel.get('type', [])
    tel['type'].append(VCARD.Telephone)
    mapping = {
        'hasValue': {
            'predicate': VCARD.hasValue,
            'objecttype': URIRef
        },
        'type': {
            'predicate': RDF.type,
            'objecttype': URIRef
        },
    }
    return _gen_mapping(graph, subject, predicate, tel, mapping)


def _add_agent(graph, subject, predicate, agent):
    agent['type'] = agent.get('type', [])
    agent['type'].append(FOAF.Agent)
    mapping = {
        'name': {
            'predicate': FOAF.name
        },
        'type': {
            'predicate': RDF.type,
            'objecttype': URIRef
        },
        'dctype': {
            'predicate': DCTERMS.type,
            'objecttype': URIRef
        },
    }
    return _gen_mapping(graph, subject, predicate, agent, mapping)


def _add_license(graph, subject, predicate, license):
    license['type'] = license.get('type', [])
    license['type'].append(DCTERMS.LicenseDocument)
    mapping = {
        'title': {
            'predicate': DCTERMS.title
        },
        'description': {
            'predicate': DCTERMS.description
        },
        'type': {
            'predicate': RDF.type,
            'objecttype': URIRef
        },
        'dctype': {
            'predicate': DCTERMS.type,
            'objecttype': URIRef
        },
        'identifier': {
            'predicate': DCTERMS.identifier,
        }
    }
    return _gen_mapping(graph, subject, predicate, license, mapping)


def _gen_mapping(graph, s, p, o, mapping):
    if 'uri' in o:
        ores = URIRef(o.get('uri'))
    else:
        ores = BNode()
    graph.add((s, p, ores))
    for k, v in mapping.items():
        if k in o:
            if 'objecttype' in v:
                objecttype = v['objecttype']
                if objecttype == 'mapping':
                    mapper = v['mapper']
            else:
                objecttype = Literal
            for ko in o[k]:
                if objecttype == 'mapping':
                    mapper(graph, ores, v['predicate'], ko)
                else:
                    oval = objecttype(ko)
                    graph.add((ores, v['predicate'], oval))
    return graph


def _add_ldf_server(graph, dataseturi, ldfurl):
    '''
    :param rdflib.graph.Graph graph: Graph that contains the Dataset.
    :param rdflib.term.URIRef subject: Uri of the Dataset.
    :param str ldfurl: Url pointing to the ldf server.
    :rtype: :class:`rdflib.graph.Graph`
    '''
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

def _add_dataset_labels(graph, subject, c):
    '''
    Add SKOS labels and a DCTERMS title to a Dataset or a Distribution of it.

    :param rdflib.graph.Graph graph: Graph that contains the Dataset.
    :param rdflib.term.URIRef subject: Uri of the Dataset or a Distribution of it.
    :param skosprovider.skos.ConceptScheme c: SKOS ConceptScheme with labels.
    :rtype: :class:`rdflib.graph.Graph`
    '''
    for l in c.labels:
        predicate = URIRef(SKOS + l.type)
        lang = extract_language(l.language)
        graph.add((subject, predicate, Literal(l.label, lang=lang)))
        if (l.type == 'prefLabel'):
            predicate = URIRef(DCTERMS.title)
            graph.add((subject, predicate, Literal(l.label, lang=lang)))
    return graph

def _add_dataset_description(graph, subject, c):
    '''
    Add SKOS notes and a DCTERMS description to a Dataset or a Distribution of it.

    :param rdflib.graph.Graph graph: Graph that contains the Dataset.
    :param rdflib.term.URIRef subject: Uri of the Dataset or a Distribution of it.
    :param skosprovider.skos.ConceptScheme c: SKOS ConceptScheme with notes.
    :rtype: :class:`rdflib.graph.Graph`
    '''
    description = None
    for n in c.notes:
        if (n.type not in ['definition', 'scopeNote']):
            continue
        predicate = URIRef(SKOS + n.type)
        lang = extract_language(n.language)
        if n.markup == 'HTML':
            html = _add_lang_to_html(n.note, lang)
            obj = Literal(html, datatype=RDF.HTML)
        else:
            obj = Literal(n.note, lang=lang)
        graph.add((subject, predicate, obj))
        if (n.type == 'definition' or description is None):
            description = obj
    if (description is not None):
        graph.add((subject, URIRef(DCTERMS.description), obj))
    return graph
