"""
add parent_comment_id to comment

Revision ID: 9f1a2b3c4d5e
Revises: 9a0f4b2c6d88
Create Date: 2025-09-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f1a2b3c4d5e'
down_revision = '9a0f4b2c6d88'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nullable parent_comment_id column
    op.add_column('comment', sa.Column('parent_comment_id', sa.Integer(), nullable=True))
    # Create index for faster lookups
    op.create_index('ix_comment_parent_comment_id', 'comment', ['parent_comment_id'], unique=False)
    # Add self-referential FK
    op.create_foreign_key('fk_comment_parent_comment', 'comment', 'comment', ['parent_comment_id'], ['id'], ondelete=None)


def downgrade() -> None:
    # Drop FK and column
    op.drop_constraint('fk_comment_parent_comment', 'comment', type_='foreignkey')
    op.drop_index('ix_comment_parent_comment_id', table_name='comment')
    op.drop_column('comment', 'parent_comment_id')


