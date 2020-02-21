"""Add infer_concept_relations column.

Revision ID: cb568ec81000
Revises: 184f1bbcb916
Create Date: 2020-02-19 09:29:17.619082
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cb568ec81000'
down_revision = '184f1bbcb916'


def upgrade():
    op.add_column(
        'concept',
        sa.Column('infer_concept_relations', sa.Boolean(), nullable=False,
                  server_default=True)
    )


def downgrade():
    op.drop_column('concept', 'infer_concept_relations')
