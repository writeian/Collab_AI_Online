"""add key_document_type to document

Revision ID: add_key_doc_type
Revises: ad7fb682d360
Create Date: 2026-02-20

Adds key_document_type column for Syllabus, Evaluation Rubric, and Other Key Documents.
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_key_doc_type'
down_revision = 'ad7fb682d360'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    # Check if column already exists (idempotent, dialect-agnostic)
    if dialect == 'sqlite':
        result = conn.execute(sa.text("PRAGMA table_info(document)"))
        cols = [row[1] for row in result.fetchall()]
        has_col = 'key_document_type' in cols
    else:
        result = conn.execute(sa.text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'document' AND column_name = 'key_document_type'
        """))
        has_col = result.fetchone() is not None

    if not has_col:
        op.add_column('document', sa.Column('key_document_type', sa.String(50), nullable=True))
        op.create_index('ix_document_key_type_room', 'document', ['room_id', 'key_document_type'], unique=False)


def downgrade():
    op.drop_index('ix_document_key_type_room', table_name='document')
    op.drop_column('document', 'key_document_type')
