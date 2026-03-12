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


class TestAddProvider:

    def _get_duri(self):
        return URIRef('https://test.atramhasis.org/void.ttl#bigdataset')

    def _get_graph(self, duri):
        g = Graph()
        g.add((duri, RDF.type, VOID.Dataset))
        return g

    def _get_provider(self, dataset=None):
        if dataset is None:
            dataset = {}
        provider_mock = Mock()
        provider_mock.get_vocabulary_id = Mock(return_value='TREES')
        provider_mock.get_metadata = Mock(return_value={'id': 'TREES', 'subject': [], 'dataset': dataset})
        cs = Mock()
        cs.uri = 'urn:x-atramhasis:conceptschemes:trees'
        cs.labels = []
        provider_mock.concept_scheme = cs
        return provider_mock

    def test_empty_provider(self):
        duri = self._get_duri()
        g = self._get_graph(duri)
        sduri = 'https://test.atramhasis.org/void.ttl#smalldataset'
        p = self._get_provider({'uri': sduri})
        homepage = 'https://test.atramhasis.org/conceptschemes/TREES'
        rdfdump = 'https://test.atramhasis.org/conceptschemes/TREES/c.rdf'
        ttldump = 'https://test.atramhasis.org/conceptschemes/TREES/c.rdf'
        req = Mock()
        req.route_url = Mock()
        req.route_url.side_effect = [
            sduri,
            homepage,
            'https://test.atramhasis.org/conceptschemes/TREES/c.rdf',
            'https://test.atramhasis.org/conceptschemes/TREES/c.ttl'
        ]
        req.registry.settings = {
            'atramhasis.ldf.enabled': True,
            'atramhasis.ldf.baseurl': 'https://test.atramhasis.org/ldf'
        }
        g = _add_provider(g, p, duri, req)
        sd = URIRef(sduri)
        assert (duri, RDF.type, VOID.Dataset) in g
        assert (sd, RDF.type, VOID.Dataset) in g
        assert (duri, VOID.subset, sd) in g
        assert (sd, DCTERMS.identifier, Literal('TREES')) in g
        assert (sd, VOID.rootResource, URIRef(p.concept_scheme.uri)) in g
        assert (sd, FOAF.homepage, URIRef(homepage)) in g
        assert (sd, VOID.dataDump, URIRef(rdfdump)) in g
        assert (sd, VOID.dataDump, URIRef(ttldump)) in g
        assert (sd, HYDRA.search, None) in g


class TestMetadataset:

    def _get_graph(self):
        return Graph()

    def test_add_empty_metadataset(self):
        metadataset = {}
        g = self._get_graph()
        uri = URIRef('https://test.atramhasis.org/void.ttl#emptyset')
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
                'https://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0'
            ]
        }
        g = self._get_graph()
        uri = URIRef('https://id.python.org/datasets/different_types_of_trees')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_metadataset(g, uri, metadataset)
        assert len(g) == 8
        assert (uri, DCTERMS.language, Literal('nl')) in g
        assert (uri, DCTERMS.language, Literal('fr')) in g
        assert (uri, DCTERMS.language, Literal('en')) in g
        assert (uri, DCTERMS.publisher, URIRef('https://id.erfgoed.net/actoren/501')) in g
        assert (uri, DCTERMS.license, URIRef('https://creativecommons.org/licenses/by/4.0/')) in g
        assert (uri, DCTERMS.license, URIRef('https://data.vlaanderen.be/doc/licentie/modellicentie-gratis-hergebruik/v1.0')) in g
        assert (uri, DCTERMS.created, Literal(date(year=2016, month=9, day=14))) in g


class TestLdfServer:

    def _get_graph(self):
        return Graph()

    def test_add_ldf_server(self):
        url = Literal('https://demo.atramhasis.org/ldf{?s,p,o}')
        g = self._get_graph()
        uri = URIRef('https://test.atramhasis.org/void.ttl#emptyset')
        g.add((uri, RDF.type, VOID.Dataset))
        g = _add_ldf_server(g, uri, url)
        assert (uri, HYDRA.search, None) in g
        assert (None, HYDRA.template, url) in g
        assert (None, HYDRA.mapping, None) in g
