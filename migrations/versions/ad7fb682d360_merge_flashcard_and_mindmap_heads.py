"""merge flashcard and mindmap heads

Revision ID: ad7fb682d360
Revises: bc1234567890, de3456789012
Create Date: 2026-02-12 11:14:42.167916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad7fb682d360'
down_revision: Union[str, Sequence[str], None] = ('bc1234567890', 'de3456789012')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
