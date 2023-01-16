"""Add conceptscheme counts

Revision ID: b04fd493106b
Revises: 3bcf11802900
Create Date: 2016-11-02 07:36:17.940810

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b04fd493106b"
down_revision = "3bcf11802900"


def upgrade():
    op.create_table(
        "conceptscheme_counts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conceptscheme_id", sa.String(), nullable=False),
        sa.Column("counted_at", sa.DateTime(), nullable=False),
        sa.Column("triples", sa.Integer, nullable=False),
        sa.Column("conceptscheme_triples", sa.Integer, nullable=False),
        sa.Column("avg_concept_triples", sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table("conceptscheme_counts")
