"""empty message

Revision ID: 5caf430627d6
Revises: f22fc607dd19
Create Date: 2019-05-09 13:08:47.903628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5caf430627d6'
down_revision = 'f22fc607dd19'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
            'invoice',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('nexudus_id', sa.Integer),
            sa.Column('timecreated', sa.Integer),
            sa.Column('amount', sa.Integer),
            sa.Column('processed', sa.Boolean),
            sa.Column('txn_id', sa.BigInteger),
            sa.Column('txn_status', sa.Text)
    )
    op.create_table(
            'log',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('log_level', sa.Text),
            sa.Column('log_message', sa.Text),
            sa.Column('invoice_id', sa.Integer, sa.ForeignKey("invoice.id")),
    )

def downgrade():
    pass
