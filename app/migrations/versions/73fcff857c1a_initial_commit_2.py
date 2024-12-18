"""initial commit_2

Revision ID: 73fcff857c1a
Revises: 
Create Date: 2024-10-22 19:22:54.960038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73fcff857c1a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Создание таблицы users
    op.create_table('users',
                    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('first_name', sa.String(), nullable=True),
                    sa.Column('last_name', sa.String(), nullable=True),
                    sa.Column('username', sa.String(), unique=True, nullable=True),
                    sa.Column('email', sa.String(), unique=True, nullable=True),
                    sa.Column('hashed_password', sa.String(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
                    sa.Column('is_admin', sa.Boolean(), default=False, nullable=True),
                    sa.Column('is_supplier', sa.Boolean(), default=False, nullable=True),
                    sa.Column('is_customer', sa.Boolean(), default=True, nullable=True),
                    )

    # Создание таблицы categories
    op.create_table('categories',
                    sa.Column('id', sa.Integer(), primary_key=True, index=True, nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('slug', sa.String(), unique=True, index=True),
                    sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
                    sa.Column('parent_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
                    )

    # Создание таблицы products
    op.create_table('products',
                    sa.Column('id', sa.Integer(), primary_key=True, index=True, nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('slug', sa.String(), unique=True, index=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=True),
                    sa.Column('image_url', sa.String(), nullable=True),
                    sa.Column('stock', sa.Integer(), nullable=True),
                    sa.Column('rating', sa.Float(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
                    sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
                    sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
                    )

    # Создание таблицы ratings
    op.create_table('ratings',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('grade', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
                    sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Создание таблицы reviews
    op.create_table('reviews',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
                    sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True),
                    sa.Column('rating_id', sa.Integer(), sa.ForeignKey('ratings.id'), nullable=True),
                    sa.Column('comment', sa.String(), nullable=True),
                    sa.Column('comment_date', sa.TIMESTAMP(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reviews')
    op.drop_table('ratings')
    # ### end Alembic commands ###
