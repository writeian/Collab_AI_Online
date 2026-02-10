"""add_difficulty_to_quiz

Revision ID: afbd40f1e68c
Revises: add_document_tables_railway
Create Date: 2026-01-02 15:06:14.230997

Adds difficulty column to quiz table for difficulty selection feature.
Difficulty can be 'easy', 'average', 'hard', or 'mixed'.
Default value is 'average' for backward compatibility.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'afbd40f1e68c'
down_revision: Union[str, Sequence[str], None] = 'add_document_tables_railway'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, table_name: str) -> bool:
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(conn)
    return any(col.get('name') == column_name for col in inspector.get_columns(table_name))


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(conn)
    return any(idx.get('name') == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    """Create quiz tables if missing and ensure difficulty column exists."""
    conn = op.get_bind()
    is_postgres = conn.dialect.name == 'postgresql'
    json_type = postgresql.JSON() if is_postgres else sa.JSON()

    # Fresh DB path: create quiz table first so downstream migrations are safe.
    if not _table_exists(conn, 'quiz'):
        op.create_table(
            'quiz',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('chat_id', sa.Integer(), nullable=False),
            sa.Column('room_id', sa.Integer(), nullable=False),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('question_count', sa.Integer(), nullable=False),
            sa.Column('context_mode', sa.String(length=20), nullable=False),
            sa.Column('difficulty', sa.String(length=20), nullable=False, server_default='average'),
            sa.Column('library_doc_ids', json_type, nullable=True),
            sa.Column('instructions', sa.Text(), nullable=True),
            sa.Column('questions', json_type, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['room_id'], ['room.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )

    if _table_exists(conn, 'quiz'):
        if not _index_exists(conn, 'quiz', 'ix_quiz_chat_id'):
            op.create_index('ix_quiz_chat_id', 'quiz', ['chat_id'], unique=False)
        if not _index_exists(conn, 'quiz', 'ix_quiz_room_id'):
            op.create_index('ix_quiz_room_id', 'quiz', ['room_id'], unique=False)
        if not _index_exists(conn, 'quiz', 'ix_quiz_created_by'):
            op.create_index('ix_quiz_created_by', 'quiz', ['created_by'], unique=False)

    # Existing DB path: add missing difficulty column idempotently.
    if _table_exists(conn, 'quiz') and not _column_exists(conn, 'quiz', 'difficulty'):
        if is_postgres:
            op.add_column(
                'quiz',
                sa.Column('difficulty', sa.String(20), nullable=False, server_default='average'),
            )
        else:
            # SQLite: add nullable, backfill values, keep model default for writes.
            op.add_column('quiz', sa.Column('difficulty', sa.String(20), nullable=True))
            op.execute(sa.text("UPDATE quiz SET difficulty = 'average' WHERE difficulty IS NULL"))

    if _table_exists(conn, 'quiz') and _column_exists(conn, 'quiz', 'difficulty'):
        op.execute(sa.text("UPDATE quiz SET difficulty = 'average' WHERE difficulty IS NULL"))

    if not _table_exists(conn, 'quiz_answer'):
        op.create_table(
            'quiz_answer',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('quiz_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('answers', json_type, nullable=False),
            sa.Column('score', sa.Integer(), nullable=True),
            sa.Column('total', sa.Integer(), nullable=True),
            sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('results', json_type, nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )

    if _table_exists(conn, 'quiz_answer'):
        if not _index_exists(conn, 'quiz_answer', 'ix_quiz_answer_quiz_id'):
            op.create_index('ix_quiz_answer_quiz_id', 'quiz_answer', ['quiz_id'], unique=False)
        if not _index_exists(conn, 'quiz_answer', 'ix_quiz_answer_user_id'):
            op.create_index('ix_quiz_answer_user_id', 'quiz_answer', ['user_id'], unique=False)


def downgrade() -> None:
    """Best-effort downgrade: only remove difficulty column if present."""
    conn = op.get_bind()
    try:
        if _table_exists(conn, 'quiz') and _column_exists(conn, 'quiz', 'difficulty'):
            op.drop_column('quiz', 'difficulty')
    except Exception:
        # Column might not exist, ignore error
        pass
