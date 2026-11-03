from datetime import date
from datetime import datetime
from datetime import timedelta

from sqlalchemy import select

from atramhasis.data.models import ConceptschemeVisitLog
from atramhasis.data.models import ConceptVisitLog
from atramhasis.scripts import prune_visit_log


class TestGetCutoff:
    def test_keep_week(self):
        cutoff = prune_visit_log.get_cutoff("week", 3, today=date(2026, 3, 15))
        assert cutoff == datetime(2026, 3, 5)

    def test_keep_month(self):
        cutoff = prune_visit_log.get_cutoff("month", 3, today=date(2026, 3, 15))
        assert cutoff == datetime(2026, 2, 12)

    def test_keep_year(self):
        cutoff = prune_visit_log.get_cutoff("year", 3, today=date(2026, 3, 15))
        assert cutoff == datetime(2025, 3, 12)

    def test_no_buffer(self):
        cutoff = prune_visit_log.get_cutoff("month", 0, today=date(2026, 3, 31))
        assert cutoff == datetime(2026, 2, 28)

    def test_defaults_to_today(self):
        cutoff = prune_visit_log.get_cutoff("week", 0)
        assert cutoff.date() == date.today() - timedelta(weeks=1)


class TestPruneVisitLog:
    def _add_visits(self, db_session):
        for visited_at in (
            datetime(2026, 1, 1, 12),
            datetime(2026, 2, 1, 0),
            datetime(2026, 2, 1, 12),
            datetime(2026, 3, 1),
        ):
            db_session.add(
                ConceptVisitLog(
                    concept_id="1",
                    conceptscheme_id="1",
                    visited_at=visited_at,
                    origin="HTML",
                )
            )
            db_session.add(
                ConceptschemeVisitLog(
                    conceptscheme_id="1", visited_at=visited_at, origin="HTML"
                )
            )
        db_session.flush()

    def _visit_dates(self, db_session, model):
        return sorted(db_session.execute(select(model.visited_at)).scalars().all())

    def test_prune_both_tables(self, db_session):
        self._add_visits(db_session)
        counts = prune_visit_log.prune_visit_log(
            db_session, datetime(2026, 2, 1), ["concept", "conceptscheme"]
        )
        assert counts == {"concept": 1, "conceptscheme": 1}
        expected = [
            datetime(2026, 2, 1, 0),
            datetime(2026, 2, 1, 12),
            datetime(2026, 3, 1),
        ]
        assert self._visit_dates(db_session, ConceptVisitLog) == expected
        assert self._visit_dates(db_session, ConceptschemeVisitLog) == expected

    def test_prune_one_table(self, db_session):
        self._add_visits(db_session)
        counts = prune_visit_log.prune_visit_log(
            db_session, datetime(2026, 2, 15), ["conceptscheme"]
        )
        assert counts == {"conceptscheme": 3}
        assert len(self._visit_dates(db_session, ConceptVisitLog)) == 4
        assert self._visit_dates(db_session, ConceptschemeVisitLog) == [
            datetime(2026, 3, 1)
        ]

    def test_dry_run(self, db_session):
        self._add_visits(db_session)
        counts = prune_visit_log.prune_visit_log(
            db_session,
            datetime(2026, 2, 15),
            ["concept", "conceptscheme"],
            dry_run=True,
        )
        assert counts == {"concept": 3, "conceptscheme": 3}
        assert len(self._visit_dates(db_session, ConceptVisitLog)) == 4
        assert len(self._visit_dates(db_session, ConceptschemeVisitLog)) == 4
