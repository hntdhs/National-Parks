"""Updated wheelchair to wheelchair_access

Revision ID: a01ce13a315c
Revises: a37025cbd36a
Create Date: 2022-08-06 14:18:18.803249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a01ce13a315c'
down_revision = 'a37025cbd36a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('campgrounds', 'wheelchair', nullable=False, new_column_name='wheelchair_access')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('campgrounds', 'wheelchair_access', nullable=False, new_column_name='wheelchair')
    # ### end Alembic commands ###
