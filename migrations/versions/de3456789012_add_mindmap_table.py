"""add_mindmap_table

Revision ID: de3456789012
Revises: cd2345678901
Create Date: 2026-01-XX 17:00:00.000000

Creates mindmap table for Mind Map Tool.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'de3456789012'
down_revision: Union[str, Sequence[str], None] = 'cd2345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, table_name: str) -> bool:
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(conn)
    return any(idx.get('name') == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    """Create mindmap table idempotently."""
    conn = op.get_bind()
    is_postgres = conn.dialect.name == 'postgresql'

    if not _table_exists(conn, 'mindmap'):
        op.create_table(
            'mindmap',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('chat_id', sa.Integer(), nullable=False),
            sa.Column('room_id', sa.Integer(), nullable=False),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('context_mode', sa.String(20), nullable=False),
            sa.Column('library_doc_ids', postgresql.JSON() if is_postgres else sa.JSON(), nullable=True),
            sa.Column('instructions', sa.Text(), nullable=True),
            sa.Column('size', sa.String(20), nullable=False),
            sa.Column('mind_map_data', postgresql.JSON() if is_postgres else sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['room_id'], ['room.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )

    if _table_exists(conn, 'mindmap'):
        if not _index_exists(conn, 'mindmap', 'ix_mindmap_chat_id'):
            op.create_index('ix_mindmap_chat_id', 'mindmap', ['chat_id'])
        if not _index_exists(conn, 'mindmap', 'ix_mindmap_room_id'):
            op.create_index('ix_mindmap_room_id', 'mindmap', ['room_id'])
        if not _index_exists(conn, 'mindmap', 'ix_mindmap_created_by'):
            op.create_index('ix_mindmap_created_by', 'mindmap', ['created_by'])


def downgrade() -> None:
    """Drop mindmap table."""
    conn = op.get_bind()
    try:
        if _table_exists(conn, 'mindmap'):
            if _index_exists(conn, 'mindmap', 'ix_mindmap_created_by'):
                op.drop_index('ix_mindmap_created_by', table_name='mindmap')
            if _index_exists(conn, 'mindmap', 'ix_mindmap_room_id'):
                op.drop_index('ix_mindmap_room_id', table_name='mindmap')
            if _index_exists(conn, 'mindmap', 'ix_mindmap_chat_id'):
                op.drop_index('ix_mindmap_chat_id', table_name='mindmap')
            op.drop_table('mindmap')
    except Exception:
        pass
