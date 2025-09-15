"""Add chat_notes table for learning context

Revision ID: a1b2c3d4e5f6
Revises: 9f1a2b3c4d5e
Create Date: 2025-09-14 23:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9f1a2b3c4d5e'
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_notes table
    op.create_table('chat_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('notes_content', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id')
    )
    
    # Create indexes for better performance
    op.create_index('ix_chat_notes_room_id', 'chat_notes', ['room_id'])
    op.create_index('ix_chat_notes_generated_at', 'chat_notes', ['generated_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_chat_notes_generated_at', table_name='chat_notes')
    op.drop_index('ix_chat_notes_room_id', table_name='chat_notes')
    
    # Drop table
    op.drop_table('chat_notes')
