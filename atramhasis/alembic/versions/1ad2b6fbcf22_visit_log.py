"""visit_log

Revision ID: 1ad2b6fbcf22
Revises: 441c5a16ef8
Create Date: 2015-07-27 13:29:04.840631

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1ad2b6fbcf22"
down_revision = "441c5a16ef8"


def upgrade():
    op.create_table(
        "conceptscheme_visit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conceptscheme_id", sa.String(), nullable=False),
        sa.Column("visited_at", sa.DateTime(), nullable=False),
        sa.Column("origin", sa.String, nullable=False),
    )
    op.create_table(
        "concept_visit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.Column("conceptscheme_id", sa.String(), nullable=False),
        sa.Column("visited_at", sa.DateTime(), nullable=False),
        sa.Column("origin", sa.String, nullable=False),
    )


def downgrade():
    op.drop_table("concept_visit_log")
    op.drop_table("conceptscheme_visit_log")
