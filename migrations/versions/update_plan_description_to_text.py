"""Update plan description to TEXT

Revision ID: update_description_text
Revises: 657ceabbb8e5
Create Date: 2026-02-24 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_description_text'
down_revision = '657ceabbb8e5'
branch_labels = None
depends_on = None


def upgrade():
    # Change description column from VARCHAR(255) to TEXT
    op.alter_column('plans', 'description',
                    existing_type=sa.String(255),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade():
    # Revert back to VARCHAR(255)
    op.alter_column('plans', 'description',
                    existing_type=sa.Text(),
                    type_=sa.String(255),
                    existing_nullable=True)
