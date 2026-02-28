"""add tutorial_completed_at to user

Revision ID: add_tutorial_completed_at
Revises: add_key_doc_type
Create Date: 2026-02-28

Adds tutorial_completed_at column for onboarding tutorial completion tracking.
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_tutorial_completed_at'
down_revision = 'add_key_doc_type'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'sqlite':
        result = conn.execute(sa.text("PRAGMA table_info(user)"))
        cols = [row[1] for row in result.fetchall()]
        has_col = 'tutorial_completed_at' in cols
    else:
        result = conn.execute(sa.text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'tutorial_completed_at'
        """))
        has_col = result.fetchone() is not None

    if not has_col:
        op.add_column('user', sa.Column('tutorial_completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('user', 'tutorial_completed_at')
