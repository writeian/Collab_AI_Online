"""Add UserModeUsage and Achievement models for gamification

Revision ID: achievement_models_001
Revises: 12722155fa55
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'achievement_models_001'
down_revision = '12722155fa55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_mode_usage table
    op.create_table('user_mode_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('mode', sa.String(length=32), nullable=False),
        sa.Column('first_used_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'room_id', 'mode', name='unique_user_room_mode')
    )
    
    # Create achievement table
    op.create_table('achievement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('achievement_type', sa.String(length=50), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'room_id', 'achievement_type', name='unique_user_room_achievement')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('achievement')
    op.drop_table('user_mode_usage') 