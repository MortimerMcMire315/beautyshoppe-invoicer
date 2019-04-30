"""consolidate tables

Revision ID: f22fc607dd19
Revises: 0d2584dcaf89
Create Date: 2019-04-26 13:56:28.480375

"""
from alembic import op
from sqlalchemy import Column, Text
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f22fc607dd19'
down_revision = '0d2584dcaf89'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('ach')
    op.rename_table('person', 'member')
    op.add_column('member',
            Column('routing_number', Text())
    )
    op.add_column('member',
            Column('account_number', Text())
    )

def downgrade():
    pass
