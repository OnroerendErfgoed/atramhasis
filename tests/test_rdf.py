# -*- coding: utf-8 -*-

import unittest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover

from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.namespace import RDF, VOID, DCTERMS, XSD, FOAF, SKOS

from atramhasis.rdf import (
    _add_metadata,
    _add_dataset_labels,
    _add_dataset_description,
    _add_provider,
    _add_ldf_server,
    HYDRA
)

from datetime import date


class AddProviderTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_duri(self):
        return URIRef('http://test.atramhasis.org/void.ttl#bigdataset')

    def _get_curi(self):
        return URIRef('http://test.atramhasis.org/dcat')

    def _get_graph(self, duri):
        g = Graph()
        g.add((duri, RDF.type, VOID.Dataset))
        return g

    def _get_provider(self, dataset = {}):
        provider_mock = Mock()
        provider_mock.get_vocabulary_id = Mock(return_value='TREES')
        provider_mock.get_metadata = Mock(return_value={'id': 'TREES', 'subject': [], 'dataset': dataset})
        cs = Mock()
        cs.uri = 'urn:x-atramhasis:conceptschemes:trees'
        cs.labels = []
        cs.notes = []
        provider_mock.concept_scheme = cs
        return provider_mock

    def testEmptyProvider(self):
        duri = self._get_duri()
        curi = self._get_curi()
        g = self._get_graph(duri)
        sduri = 'http://test.atramhasis.org/void.ttl#smalldataset'
        p = self._get_provider({'uri': sduri})
        homepage = 'http://test.atramhasis.org/conceptschemes/TREES'
        rdfdump = 'http://test.atramhasis.org/conceptschemes/TREES/c.rdf'
        ttldump = 'http://test.atramhasis.org/conceptschemes/TREES/c.rdf'
        req = Mock()
        req.route_url = Mock()
        req.route_url.side_effect = [
            sduri,
            homepage,
            'http://test.atramhasis.org/conceptschemes/TREES/c.rdf',
            'http://test.atramhasis.org/conceptschemes/TREES/c.ttl'
        ]
        req.registry.settings = {
            'atramhasis.ldf.enabled': True,
            'atramhasis.ldf.baseurl': 'http://test.atramhasis.org/ldf'
        }
        g = _add_provider(g, p, duri, curi, req)
        sd = URIRef(sduri)
        self.assertIn((duri, RDF.type, VOID.Dataset), g)
        self.assertIn((sd, RDF.type, VOID.Dataset), g)
        self.assertIn((duri, VOID.subset, sd), g)
        self.assertIn((sd, DCTERMS.identifier, Literal('TREES')), g)
        self.assertIn((sd, VOID.rootResource, URIRef(p.concept_scheme.uri)), g)
        self.assertIn((sd, FOAF.homepage, URIRef(homepage)), g)
        self.assertIn((sd, VOID.dataDump, URIRef(rdfdump)), g)
        self.assertIn((sd, VOID.dataDump, URIRef(ttldump)), g)
        self.assertIn((sd, HYDRA.search, None), g)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_graph(self):
        return Graph()

    def test_add_empty_metadata(self):
        metadataset = {}
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadata(g, uri, metadataset)
        self.assertEquals(1, len(g))

    def test_add_metadata(self):
        metadataset = {
            'publisher': [{
                'uri': 'https://id.erfgoed.net/actoren/501',
                'name': ['Onroerend Erfgoed'],
                'type': ['http://xmlns.com/foaf/0.1/Organization']
            }],
            'created': [date(2016,9,14)],
            'language': ['nl', 'en', 'fr'],
            'license': [{
                'uri': 'https://creativecommons.org/licenses/by/4.0/',
            }, {
                'uri': 'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0',
            }]
        }
        g = self._get_graph()
        uri = URIRef('http://id.python.org/datasets/different_types_of_trees')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadata(g, uri, metadataset)
        #self.assertEquals(8, len(g))
        self.assertIn((uri, DCTERMS.language, Literal('nl')), g)
        self.assertIn((uri, DCTERMS.language, Literal('fr')), g)
        self.assertIn((uri, DCTERMS.language, Literal('en')), g)
        self.assertIn((uri, DCTERMS.publisher, URIRef('https://id.erfgoed.net/actoren/501')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('https://creativecommons.org/licenses/by/4.0/')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0')), g)
        self.assertIn((uri, DCTERMS.created, Literal(date(2016,9,14))), g)

class LdfServerTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_graph(self):
        return Graph()

    def test_add_ldf_server(self):
        url = Literal('http://demo.atramhasis.org/ldf{?s,p,o}')
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_ldf_server(g, uri, url)
        self.assertIn((uri, HYDRA.search, None), g)
        self.assertIn((None, HYDRA.template, url), g)
        self.assertIn((None, HYDRA.mapping, None), g)

class LabelsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_graph(self):
        return Graph()

    def test_add_empty_labels(self):
        cs = Mock()
        cs.labels = []
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_dataset_labels(g, uri, cs)
        self.assertIn((uri, RDF.type, VOID.Dataset), g)
        self.assertNotIn((uri, DCTERMS.title, None), g)
        self.assertNotIn((uri, SKOS.prefLabel, None), g)

    def test_add_prefLabel(self):
        l = Mock()
        l.type = 'prefLabel'
        l.language = 'en'
        l.label = 'My Set'
        cs = Mock()
        cs.labels = [l]
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_dataset_labels(g, uri, cs)
        self.assertIn((uri, RDF.type, VOID.Dataset), g)
        self.assertIn((uri, SKOS.prefLabel, Literal('My Set', lang='en')), g)
        self.assertIn((uri, DCTERMS.title, Literal('My Set', lang='en')), g)

    def test_add_altLabel(self):
        l = Mock()
        l.type = 'altLabel'
        l.language = 'en'
        l.label = 'My Alt Set'
        cs = Mock()
        cs.labels = [l]
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_dataset_labels(g, uri, cs)
        self.assertIn((uri, RDF.type, VOID.Dataset), g)
        self.assertIn((uri, SKOS.altLabel, Literal('My Alt Set', lang='en')), g)
        self.assertNotIn((uri, DCTERMS.title, None), g)

class DescriptionTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_graph(self):
        return Graph()

    def test_add_empty_notes(self):
        cs = Mock()
        cs.notes = []
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_dataset_description(g, uri, cs)
        self.assertIn((uri, RDF.type, VOID.Dataset), g)

    def test_add_notes_with_definition(self):
        n = Mock()
        n.type = 'definition'
        n.language = 'en'
        n.note = 'My Set Note'
        n.markup = None
        cs = Mock()
        cs.notes = [n]
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_dataset_description(g, uri, cs)
        self.assertIn((uri, RDF.type, VOID.Dataset), g)
        self.assertIn((uri, SKOS.definition, Literal('My Set Note', lang='en')), g)
        self.assertIn((uri, DCTERMS.description, Literal('My Set Note', lang='en')), g)

