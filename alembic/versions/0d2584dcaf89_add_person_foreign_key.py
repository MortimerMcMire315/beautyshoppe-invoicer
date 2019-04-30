"""add person foreign key

Revision ID: 0d2584dcaf89
Revises:
Create Date: 2019-04-26 13:09:21.256866

"""
from alembic import op
from sqlalchemy import Column, ForeignKey, INTEGER
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d2584dcaf89'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ach',
            Column('person_id', INTEGER, ForeignKey('person.id'))
    )


def downgrade():
    op.drop_column(Column('person_id', INTEGER, ForeignKey('person.id')))
    pass
