"""Insert data into products table

Revision ID: 84c830a515ce
Revises: 8bc4e594a952
Create Date: 2026-11-18 17:09:00.277808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84c830a515ce'
down_revision = '8bc4e594a952'
branch_labels = None
depends_on = None



def upgrade():
    categories_table = sa.table(
        'categories',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String)
    )

    products_table = sa.table(
        'products',
        sa.column('name', sa.String),
        sa.column('price', sa.Float),
        sa.column('active', sa.Boolean),
        sa.column('category_id', sa.Integer)
    )

    op.bulk_insert(categories_table, [
        {'id': 3, 'name': 'Electronics'},
        {'id': 4, 'name': 'Books'},
        {'id': 5, 'name': 'Clothing'},
    ])

    op.bulk_insert(products_table, [
        {'name': 'Laptop', 'price': 1200.0, 'active': True, 'category_id': 3},
        {'name': 'Smartphone', 'price': 800.0, 'active': True, 'category_id': 3},
        {'name': 'Novel', 'price': 20.0, 'active': True, 'category_id': 4},
        {'name': 'T-Shirt', 'price': 25.0, 'active': False, 'category_id': 5},
    ])


def downgrade():
    op.execute("""
        DELETE FROM products
        WHERE name IN ('Laptop', 'Smartphone', 'Novel', 'T-Shirt');
    """)

    op.execute("""
        DELETE FROM categories
        WHERE name IN ('Electronics', 'Books', 'Clothing');
    """)
