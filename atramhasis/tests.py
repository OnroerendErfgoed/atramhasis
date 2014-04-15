import unittest
import transaction

from pyramid import testing

from .models import DBSession

from .scaffolds import AtramhasisTemplate, AtramhasisDemoTemplate


class TestMyViewSuccessCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        print('info' + info['project'])
        self.assertEqual(info['project'], 'atramhasis')


class TestScaffolding(unittest.TestCase):
    def test_scaffolding(self):
        atemp = AtramhasisTemplate('test')
        atempdemo = AtramhasisDemoTemplate('demo')
        self.assertEqual(atemp.summary, 'Create an Atramhasis implementation')
        self.assertEqual(atempdemo.summary, 'Create an Atramhasis demo')
        self.assertEqual(atemp.name, 'test')
        self.assertEqual(atempdemo.name, 'demo')