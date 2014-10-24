"""add skos matches

Revision ID: 441c5a16ef8
Revises: 4f1ee5c9c08
Create Date: 2014-10-24 11:04:10.310845

"""

# revision identifiers, used by Alembic.
revision = '441c5a16ef8'
down_revision = '4f1ee5c9c08'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('matchtype',
                    sa.Column('name', sa.String(length=20), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('name')
                    )
    op.create_table('match',
                    sa.Column('uri', sa.String(length=512), nullable=False),
                    sa.Column('concept_id', sa.Integer, nullable=False),
                    sa.Column('matchtype_id', sa.String(length=20), nullable=False),
                    sa.ForeignKeyConstraint(['concept_id'], ['concept.id'], ),
                    sa.ForeignKeyConstraint(['matchtype_id'], ['matchtype.name'], ),
                    sa.PrimaryKeyConstraint('uri', 'concept_id', 'matchtype_id')
                    )


def downgrade():
    op.drop_table('match')
    op.drop_table('matchtype')
