"""Add infer_concept_relations column.

Revision ID: cb568ec81000
Revises: 184f1bbcb916
Create Date: 2020-02-19 09:29:17.619082
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cb568ec81000"
down_revision = "184f1bbcb916"


def upgrade():
    op.add_column(
        "concept",
        sa.Column(
            "infer_concept_relations",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )


def downgrade():
    with op.batch_alter_table("concept") as batch_op:
        batch_op.drop_column("infer_concept_relations")
