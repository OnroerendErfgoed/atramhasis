import os

from paste.deploy import appconfig
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import NoteType
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.models import Visitation

from atramhasis.scripts import delete_scheme
from tests import DbTest
from tests import db_session
from tests import fill_db
from tests import setup_db

TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, 'conf_test.ini'))


def setUpModule():
    setup_db()
    fill_db()


class DeleteSchemeTest(DbTest):

    def test_delete(self):
        with db_session() as session:
            for id in range(1, 10):
                delete_scheme.delete_scheme(settings, id)
            assert len(session.query(ConceptScheme).all()) == 0
            assert len(session.query(Concept).all()) == 0
            assert len(session.query(Collection).all()) == 0
            assert len(session.query(Note).all()) == 0
            assert len(session.query(Source).all()) == 0
            assert len(session.query(Visitation).all()) == 0
            assert len(session.query(Label).all()) == 0
            assert len(session.query(LabelType).all()) != 0
            assert len(session.query(NoteType).all()) != 0
            assert len(session.query(Language).all()) != 0

