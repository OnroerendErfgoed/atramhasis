import unittest
import tempfile
import os

from atramhasis.scaffolds import AtramhasisTemplate, AtramhasisDemoTemplate, copy_dir_to_scaffold


class TestScaffolding(unittest.TestCase):
    def test_scaffolding(self):
        atemp = AtramhasisTemplate('test')
        atempdemo = AtramhasisDemoTemplate('demo')
        self.assertEqual(atemp.summary, 'Create an Atramhasis implementation')
        self.assertEqual(atempdemo.summary, 'Create an Atramhasis demo')
        self.assertEqual(atemp.name, 'test')
        self.assertEqual(atempdemo.name, 'demo')

    def test_copy_locale(self):
        temp_dir = tempfile.mkdtemp()
        copy_dir_to_scaffold(temp_dir, 'package', 'locale')
        result_dir = os.path.join(temp_dir, 'package', 'locale')
        self.assertTrue(os.path.exists(result_dir))
        size = len([name for name in os.listdir(result_dir)])
        self.assertTrue(size > 0)
