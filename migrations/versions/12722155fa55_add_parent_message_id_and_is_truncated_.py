"""Add parent_message_id and is_truncated to message

Revision ID: 12722155fa55
Revises: dade1def113a
Create Date: 2025-07-21 13:59:10.919987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12722155fa55'
down_revision: Union[str, Sequence[str], None] = 'dade1def113a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('message', sa.Column('parent_message_id', sa.Integer(), nullable=True))
    op.add_column('message', sa.Column('is_truncated', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Only create foreign key if not using SQLite (which doesn't support ALTER TABLE for constraints)
    connection = op.get_bind()
    if connection.dialect.name != 'sqlite':
        op.create_foreign_key(
            'fk_message_parent_message_id_message',
            'message', 'message',
            ['parent_message_id'], ['id'],
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Only drop foreign key if not using SQLite
    connection = op.get_bind()
    if connection.dialect.name != 'sqlite':
        op.drop_constraint('fk_message_parent_message_id_message', 'message', type_='foreignkey')
    op.drop_column('message', 'parent_message_id')
    op.drop_column('message', 'is_truncated')
    # ### end Alembic commands ###
