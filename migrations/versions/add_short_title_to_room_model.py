"""add short_title to room model

Revision ID: f1a2b3c4d5e6
Revises: 55f5aa3fe9e7
Create Date: 2025-09-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '55f5aa3fe9e7'
branch_labels = None
depends_on = None

def upgrade():
    # Add short_title column to room table
    op.add_column('room', sa.Column('short_title', sa.String(length=50), nullable=True))

def downgrade():
    # Remove short_title column
    op.drop_column('room', 'short_title')
