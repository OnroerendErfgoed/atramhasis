"""Add markup to source.

Revision ID: 3bcf11802900
Revises: 1a4d62b02630
Create Date: 2016-05-25 14:31:51.579412

"""

# revision identifiers, used by Alembic.
revision = '3bcf11802900'
down_revision = '1a4d62b02630'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('source', sa.Column('markup', sa.String(20)))


def downgrade():
    op.drop_column('source', 'markup')
