"""allow more null values in parks

Revision ID: 0a092ef7467c
Revises: a01ce13a315c
Create Date: 2022-08-11 15:15:42.378720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a092ef7467c'
down_revision = 'a01ce13a315c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('articles', 'park_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.create_foreign_key(None, 'articles', 'parks', ['park_id'], ['id'], ondelete='CASCADE')
#    op.drop_column('favorited', 'favorited_park_id')
    op.alter_column('parks', 'image_title',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('parks', 'image_altText',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('parks', 'image_url',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('parks', 'weather_info',
               existing_type=sa.TEXT(),
               nullable=True)
    #op.drop_column('visited', 'visited_park_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('visited', sa.Column('visited_park_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.alter_column('parks', 'weather_info',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('parks', 'image_url',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('parks', 'image_altText',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('parks', 'image_title',
               existing_type=sa.TEXT(),
               nullable=False)
    #op.add_column('favorited', sa.Column('favorited_park_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_constraint(None, 'articles', type_='foreignkey')
    op.alter_column('articles', 'park_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###