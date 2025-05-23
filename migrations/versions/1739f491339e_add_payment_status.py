"""add payment status

Revision ID: 1739f491339e
Revises: fd73b3b233a7
Create Date: 2025-05-08 19:27:23.764210

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1739f491339e'
down_revision = 'fd73b3b233a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction_items', schema=None) as batch_op:
        batch_op.drop_column('payment_status')

    # ### end Alembic commands ###
