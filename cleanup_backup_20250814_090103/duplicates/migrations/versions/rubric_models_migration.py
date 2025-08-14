"""Add rubric models for learning step assessment

Revision ID: rubric_models_001
Revises: a8c4d37510b7
Create Date: 2025-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'rubric_models_001'
down_revision = 'a8c4d37510b7'
branch_labels = None
depends_on = None

def upgrade():
    # Create rubric_criterion table
    op.create_table('rubric_criterion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('step_key', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_id', 'step_key', 'name', name='unique_room_step_criterion')
    )
    
    # Create rubric_level table
    op.create_table('rubric_level',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('criterion_id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('examples', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['criterion_id'], ['rubric_criterion.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create room_rubric table
    op.create_table('room_rubric',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('step_key', sa.String(length=32), nullable=False),
        sa.Column('progression_threshold', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_id', 'step_key', name='unique_room_step_rubric')
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('room_rubric')
    op.drop_table('rubric_level')
    op.drop_table('rubric_criterion') 