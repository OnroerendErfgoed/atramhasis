import unittest

from atramhasis.scaffolds import AtramhasisTemplate, AtramhasisDemoTemplate


class TestScaffolding(unittest.TestCase):
    def test_scaffolding(self):
        atemp = AtramhasisTemplate('test')
        atempdemo = AtramhasisDemoTemplate('demo')
        self.assertEqual(atemp.summary, 'Create an Atramhasis implementation')
        self.assertEqual(atempdemo.summary, 'Create an Atramhasis demo')
        self.assertEqual(atemp.name, 'test')
        self.assertEqual(atempdemo.name, 'demo')
