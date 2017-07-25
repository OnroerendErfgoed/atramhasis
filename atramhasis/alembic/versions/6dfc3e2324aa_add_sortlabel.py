"""add_sortlabel

Revision ID: 6dfc3e2324aa
Revises: b04fd493106b
Create Date: 2017-07-04 13:53:00.064535

"""

# revision identifiers, used by Alembic.
revision = '6dfc3e2324aa'
down_revision = 'b04fd493106b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

labeltype_table = sa.Table(
    'labeltype',
    sa.MetaData(),
    sa.Column('name', sa.String),
    sa.Column('description', sa.String)
)


def upgrade():

    op.bulk_insert(
        labeltype_table,
        [{'name': 'sortLabel', 'description': 'A sorting label.'}]
    )


def downgrade():
    connection = op.get_bind()
    session = Session(bind=connection)
    connection.execute(
        labeltype_table.delete().where(labeltype_table.c.name == 'sortLabel')
    )
    session.flush()