"""Add markup to source.

Revision ID: 3bcf11802900
Revises: 1a4d62b02630
Create Date: 2016-05-25 14:31:51.579412

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3bcf11802900"
down_revision = "1a4d62b02630"


def upgrade():
    op.add_column("source", sa.Column("markup", sa.String(20)))


def downgrade():
    with op.batch_alter_table("source") as batch_op:
        batch_op.drop_column("markup")
