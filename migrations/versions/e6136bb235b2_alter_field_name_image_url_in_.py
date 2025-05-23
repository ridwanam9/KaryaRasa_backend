"""alter field name image_url in transaction

Revision ID: e6136bb235b2
Revises: 9d0d171011d7
Create Date: 2025-04-28 22:33:39.353249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6136bb235b2'
down_revision = '9d0d171011d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))
        batch_op.drop_column('product_image')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_image', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###
