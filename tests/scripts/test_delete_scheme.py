import pytest
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


class TestDeleteScheme:
    def test_delete(self, db_session):
        query = select(ConceptScheme.id)
        scheme_ids = db_session.execute(query).scalars().all()
        for scheme_id in scheme_ids:
            delete_scheme.delete_scheme(db_session, scheme_id)

        assert len(db_session.execute(select(ConceptScheme)).all()) == 0
        assert len(db_session.execute(select(Concept)).all()) == 0
        assert len(db_session.execute(select(Collection)).all()) == 0
        assert len(db_session.execute(select(Note)).all()) == 0
        assert len(db_session.execute(select(Source)).all()) == 0
        assert len(db_session.execute(select(Visitation)).all()) == 0
        assert len(db_session.execute(select(Label)).all()) == 0
        assert len(db_session.execute(select(LabelType)).all()) != 0
        assert len(db_session.execute(select(NoteType)).all()) != 0
        assert len(db_session.execute(select(Language)).all()) != 0
