# -*- coding: utf-8 -*-
import os
import sys
from pyramid.paster import get_appsettings
import unittest

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from skosprovider_sqlalchemy.models import Base
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from skosprovider.utils import dict_dumper

from atramhasis.scripts import import_file

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))
test_data_rdf = os.path.join(here, '../', 'tests/data/trees.xml')
test_data_json = os.path.join(here, '../', 'tests/data/trees.json')


class ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings['sqlalchemy.url'] = 'sqlite:///%s/dbtest.sqlite' % here
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        Base.metadata.drop_all(cls.engine)
        Base.metadata.create_all(cls.engine)

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        self.session_maker = sessionmaker(
            bind=self.engine,
            extension=ZopeTransactionExtension()
        )

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _check_trees(self):
        sql_prov = SQLAlchemyProvider({'id': 'TREES', 'conceptscheme_id': 1}, self.session_maker)
        dump = dict_dumper(sql_prov)

        self.assertEqual(len(dump), 3)
        obj_1 = [item for item in dump if item['uri'] == 'http://id.trees.org/2'][0]
        self.assertEqual(obj_1['broader'], [])
        self.assertEqual(obj_1['id'], 2)
        self.assertEqual(obj_1['member_of'], [3])
        self.assertEqual(obj_1['narrower'], [])
        label_en = [label for label in obj_1['labels'] if label['language'] == 'en'][0]
        self.assertDictEqual(label_en, {'label': 'The Chestnut', 'language': 'en', 'type': 'prefLabel'})
        label_nl = [label for label in obj_1['labels'] if label['language'] == 'nl'][0]
        self.assertDictEqual(label_nl, {'label': 'De Paardekastanje', 'language': 'nl', 'type': 'altLabel'})
        label_fr = [label for label in obj_1['labels'] if label['language'] == 'fr'][0]
        self.assertDictEqual(label_fr, {'label': u'la châtaigne', 'language': 'fr', 'type': 'altLabel'})
        self.assertDictEqual(obj_1['notes'][0],
                             {'language': 'en', 'note': 'A different type of tree.', 'type': 'definition'})

    def test_import_rdf(self):
        sys.argv = ['import_file', '--from', test_data_rdf, '--to', settings['sqlalchemy.url']]
        import_file.main(sys.argv)

    def test_import_json(self):
        sys.argv = ['import_file', '--from', test_data_json, '--to', settings['sqlalchemy.url']]
        import_file.main(sys.argv)




