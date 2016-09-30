# -*- coding: utf-8 -*-

import unittest

from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.namespace import RDF, VOID, DCTERMS, XSD

from atramhasis.rdf import _add_metadataset

from datetime import date

class MetadatasetTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_graph(self):
        return Graph()

    def test_add_empty_metadataset(self):
        metadataset = {}
        g = self._get_graph()
        uri = URIRef('http://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadataset(g, uri, metadataset)
        self.assertEquals(1, len(g))

    def test_add_metadataset(self):
        metadataset = {
            'publisher': ['https://id.erfgoed.net/actoren/501'],
            'created': [date(2016,9,14)],
            'language': ['nl', 'en', 'fr'],
            'license': [
                'https://creativecommons.org/licenses/by/4.0/',
                'https://id.erfgoed.net/vocab/licences#GODL'
            ]
        }
        g = self._get_graph()
        uri = URIRef('http://id.python.org/datasets/different_types_of_trees')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadataset(g, uri, metadataset)
        self.assertEquals(8, len(g))
        self.assertIn((uri, DCTERMS.language, Literal('nl')), g)
        self.assertIn((uri, DCTERMS.language, Literal('fr')), g)
        self.assertIn((uri, DCTERMS.language, Literal('en')), g)
        self.assertIn((uri, DCTERMS.publisher, URIRef('https://id.erfgoed.net/actoren/501')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('https://creativecommons.org/licenses/by/4.0/')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('https://id.erfgoed.net/vocab/licences#GODL')), g)
        self.assertIn((uri, DCTERMS.created, Literal(date(2016,9,14))), g)

