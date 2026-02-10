"""merge flashcard heads

Revision ID: ee4567890123
Revises: bc1234567890, de3456789012
Create Date: 2026-02-10 11:30:00.000000
"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'ee4567890123'
down_revision: Union[str, Sequence[str], None] = ('bc1234567890', 'de3456789012')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge branch heads; no schema changes."""
    pass


def downgrade() -> None:
    """No-op downgrade for merge revision."""
    pass

