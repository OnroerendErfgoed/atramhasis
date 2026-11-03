import argparse
from datetime import date
from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select

from atramhasis import utils
from atramhasis.data.models import ConceptschemeVisitLog
from atramhasis.data.models import ConceptVisitLog

log = logging.getLogger(__name__)

VISIT_LOG_MODELS = {
    "concept": ConceptVisitLog,
    "conceptscheme": ConceptschemeVisitLog,
}


def get_cutoff(keep, buffer_days, today=None):
    """
    Calculate the moment before which visit log rows can be removed.

    Uses the same rolling periods as
    :meth:`atramhasis.data.datamanagers.AuditManager._get_first_day`.

    :param keep: 'week', 'month' or 'year'
    :param buffer_days: extra days kept on top of `keep`
    :param today: the reference date, defaults to the current date
    :return: (datetime) rows visited before this moment can be removed
    """
    today = today or date.today()
    cutoff = today - relativedelta(**{f"{keep}s": 1}) - relativedelta(days=buffer_days)
    return datetime.combine(cutoff, datetime.min.time())


def prune_visit_log(session, cutoff, tables, dry_run=False):
    """
    Remove visit log rows older than the cutoff.

    :param session: a database session
    :param cutoff: (datetime) rows visited before this moment are removed
    :param tables: iterable of 'concept' and/or 'conceptscheme'
    :param dry_run: only count the rows that would be removed
    :return: (dict) number of (to be) removed rows per table
    """
    counts = {}
    for table in tables:
        model = VISIT_LOG_MODELS[table]
        if dry_run:
            counts[table] = session.execute(
                select(func.count()).where(model.visited_at < cutoff)
            ).scalar_one()
        else:
            counts[table] = session.execute(
                delete(model).where(model.visited_at < cutoff)
            ).rowcount
    return counts


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Remove old rows from the concept and conceptscheme visit logs.",
        usage="prune_visit_log development.ini --keep year --buffer-days 3",
    )
    parser.add_argument(
        "settings_file", help="<The location of the settings file>#<app-name>"
    )
    parser.add_argument(
        "--keep",
        choices=["week", "month", "year"],
        default="year",
        help="How much data to keep (default: year)",
    )
    parser.add_argument(
        "--buffer-days",
        type=int,
        default=3,
        help="Extra days kept on top of --keep (default: 3)",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        choices=list(VISIT_LOG_MODELS),
        default=list(VISIT_LOG_MODELS),
        help="Which visit log tables to prune (default: both)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report how many rows would be deleted",
    )
    args = parser.parse_args()
    if args.buffer_days < 0:
        parser.error("--buffer-days must not be negative")

    config_uri = args.settings_file
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    if args.keep == "week":
        log.warning(
            "Keeping only a week of visits: the default templates show the most "
            "popular concepts of the last month, which will be incomplete."
        )

    cutoff = get_cutoff(args.keep, args.buffer_days)
    with utils.db_session(settings) as session:
        counts = prune_visit_log(session, cutoff, args.tables, args.dry_run)

    for table, count in counts.items():
        if args.dry_run:
            print(
                f"{table}_visit_log: {count} rows visited before {cutoff} would be deleted"
            )
        else:
            print(f"{table}_visit_log: {count} rows visited before {cutoff} deleted")


if __name__ == "__main__":  # pragma: no cover
    main()
