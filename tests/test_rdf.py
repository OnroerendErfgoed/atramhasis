import unittest
from datetime import date
from unittest.mock import Mock

from rdflib import DCTERMS
from rdflib import FOAF
from rdflib import Graph
from rdflib import RDF
from rdflib import VOID
from rdflib.term import Literal
from rdflib.term import URIRef

from atramhasis.rdf import HYDRA
from atramhasis.rdf import _add_ldf_server
from atramhasis.rdf import _add_metadataset
from atramhasis.rdf import _add_provider


class AddProviderTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_duri(self):
        return URIRef('http://test.atramhasis.org/void.ttl#bigdataset')

    def _get_graph(self, duri):
        g = Graph()
        g.add((duri, RDF.type, VOID.Dataset))
        return g

    def _get_provider(self, dataset={}):
        provider_mock = Mock()
        provider_mock.get_vocabulary_id = Mock(return_value='TREES')
        provider_mock.get_metadata = Mock(return_value={'id': 'TREES', 'subject': [], 'dataset': dataset})
        cs = Mock()
        cs.uri = 'urn:x-atramhasis:conceptschemes:trees'
        cs.labels = []
        provider_mock.concept_scheme = cs
        return provider_mock

    def testEmptyProvider(self):
        duri = self._get_duri()
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
        g = _add_provider(g, p, duri, req)
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
        assert len(g) == 1

    def test_add_metadataset(self):
        metadataset = {
            'publisher': ['https://id.erfgoed.net/actoren/501'],
            'created': [date(year=2016, month=9, day=14)],
            'language': ['nl', 'en', 'fr'],
            'license': [
                'https://creativecommons.org/licenses/by/4.0/',
                'http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
            ]
        }
        g = self._get_graph()
        uri = URIRef('http://id.python.org/datasets/different_types_of_trees')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadataset(g, uri, metadataset)
        assert len(g) == 8
        self.assertIn((uri, DCTERMS.language, Literal('nl')), g)
        self.assertIn((uri, DCTERMS.language, Literal('fr')), g)
        self.assertIn((uri, DCTERMS.language, Literal('en')), g)
        self.assertIn((uri, DCTERMS.publisher, URIRef('https://id.erfgoed.net/actoren/501')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('https://creativecommons.org/licenses/by/4.0/')), g)
        self.assertIn((uri, DCTERMS.license, URIRef('http://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0')), g)
        self.assertIn((uri, DCTERMS.created, Literal(date(year=2016, month=9, day=14))), g)


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
