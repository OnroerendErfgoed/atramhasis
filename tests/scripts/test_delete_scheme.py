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
from sqlalchemy import select

from atramhasis.scripts import delete_scheme
from tests import DbTest
from tests import db_session
from tests import fill_db
from tests import setup_db

TEST_DIR = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(TEST_DIR, '../conf_test.ini'))


def setUpModule():
    setup_db()
    fill_db()


class DeleteSchemeTest(DbTest):

    def test_delete(self):
        with db_session() as session:
            for scheme_id in range(1, 10):
                delete_scheme.delete_scheme(session, scheme_id)
            assert len(session.execute(select(ConceptScheme)).all()) == 0
            assert len(session.execute(select(Concept)).all()) == 0
            assert len(session.execute(select(Collection)).all()) == 0
            assert len(session.execute(select(Note)).all()) == 0
            assert len(session.execute(select(Source)).all()) == 0
            assert len(session.execute(select(Visitation)).all()) == 0
            assert len(session.execute(select(Label)).all()) == 0
            assert len(session.execute(select(LabelType)).all()) != 0
            assert len(session.execute(select(NoteType)).all()) != 0
            assert len(session.execute(select(Language)).all()) != 0
