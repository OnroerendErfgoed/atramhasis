import unittest
import transaction

from pyramid import testing

from .models import DBSession

from .scaffolds import AtramhasisTemplate, AtramhasisDemoTemplate


class TestMyViewSuccessCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_passing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'atramhasis')


class TestMyViewFailureCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_failing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info.status_int, 500)


class TestScaffolding(unittest.TestCase):
    def test_scaffolding(self):
        atemp= AtramhasisTemplate('test')
        atempdemo= AtramhasisDemoTemplate('demo')
        self.assertEqual(atemp.summary, 'Create an Atramhasis implementation')
        self.assertEqual(atempdemo.summary, 'Create an Atramhasis demo')
        self.assertEqual(atemp.name, 'test')
        self.assertEqual(atempdemo.name, 'demo')