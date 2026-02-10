"""add_flashcard_tables

Revision ID: cd2345678901
Revises: afbd40f1e68c
Create Date: 2026-01-02 17:00:00.000000

Creates flashcard_set and flashcard_session tables for Flashcards Tool.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cd2345678901'
down_revision: Union[str, Sequence[str], None] = 'afbd40f1e68c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, table_name: str) -> bool:
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(conn)
    return any(idx.get('name') == index_name for idx in inspector.get_indexes(table_name))


def _has_unique_on_column(conn, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(conn)
    for idx in inspector.get_indexes(table_name):
        if idx.get('unique') and idx.get('column_names') == [column_name]:
            return True
    for uq in inspector.get_unique_constraints(table_name):
        if uq.get('column_names') == [column_name]:
            return True
    return False


def upgrade() -> None:
    """Create flashcard_set and flashcard_session tables idempotently."""
    conn = op.get_bind()
    is_postgres = conn.dialect.name == 'postgresql'

    if not _table_exists(conn, 'flashcard_set'):
        op.create_table(
            'flashcard_set',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('chat_id', sa.Integer(), nullable=False),
            sa.Column('room_id', sa.Integer(), nullable=False),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('context_mode', sa.String(20), nullable=False),
            sa.Column('library_doc_ids', postgresql.JSON() if is_postgres else sa.JSON(), nullable=True),
            sa.Column('instructions', sa.Text(), nullable=True),
            sa.Column('display_mode', sa.String(20), nullable=False),
            sa.Column('grid_size', sa.String(10), nullable=True),
            sa.Column('is_infinite', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('cards', postgresql.JSON() if is_postgres else sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['room_id'], ['room.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )

    if _table_exists(conn, 'flashcard_set'):
        if not _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_chat_id'):
            op.create_index('ix_flashcard_set_chat_id', 'flashcard_set', ['chat_id'])
        if not _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_room_id'):
            op.create_index('ix_flashcard_set_room_id', 'flashcard_set', ['room_id'])
        if not _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_created_by'):
            op.create_index('ix_flashcard_set_created_by', 'flashcard_set', ['created_by'])

    if not _table_exists(conn, 'flashcard_session'):
        op.create_table(
            'flashcard_session',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('flashcard_set_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.String(64), nullable=False),
            sa.Column('cursor_state', postgresql.JSON() if is_postgres else sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['flashcard_set_id'], ['flashcard_set.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('session_id'),
        )

    if _table_exists(conn, 'flashcard_session'):
        if not _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_flashcard_set_id'):
            op.create_index('ix_flashcard_session_flashcard_set_id', 'flashcard_session', ['flashcard_set_id'])
        if not _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_user_id'):
            op.create_index('ix_flashcard_session_user_id', 'flashcard_session', ['user_id'])
        if not _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_session_id') and not _has_unique_on_column(conn, 'flashcard_session', 'session_id'):
            op.create_index('ix_flashcard_session_session_id', 'flashcard_session', ['session_id'], unique=True)


def downgrade() -> None:
    """Drop flashcard_set and flashcard_session tables."""
    conn = op.get_bind()
    try:
        if _table_exists(conn, 'flashcard_session'):
            if _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_session_id'):
                op.drop_index('ix_flashcard_session_session_id', table_name='flashcard_session')
            if _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_user_id'):
                op.drop_index('ix_flashcard_session_user_id', table_name='flashcard_session')
            if _index_exists(conn, 'flashcard_session', 'ix_flashcard_session_flashcard_set_id'):
                op.drop_index('ix_flashcard_session_flashcard_set_id', table_name='flashcard_session')
            op.drop_table('flashcard_session')
    except Exception:
        pass

    try:
        if _table_exists(conn, 'flashcard_set'):
            if _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_created_by'):
                op.drop_index('ix_flashcard_set_created_by', table_name='flashcard_set')
            if _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_room_id'):
                op.drop_index('ix_flashcard_set_room_id', table_name='flashcard_set')
            if _index_exists(conn, 'flashcard_set', 'ix_flashcard_set_chat_id'):
                op.drop_index('ix_flashcard_set_chat_id', table_name='flashcard_set')
            op.drop_table('flashcard_set')
    except Exception:
        pass
