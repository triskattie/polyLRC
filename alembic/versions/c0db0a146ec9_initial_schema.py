"""initial schema

Revision ID: c0db0a146ec9
Revises: 
Create Date: 2026-01-21 22:56:37.270072

NOTE: This migration was originally auto-generated with an Integer-based 'users'
table that was superseded in the very next migration (35d0060ebab4) by a UUID-based
redesign. To avoid a duplicate-table conflict on upgrade, the actual table creation
has been moved entirely into 35d0060ebab4. This revision is kept as a placeholder
to preserve the migration chain.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c0db0a146ec9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass  # Table creation moved to 35d0060ebab4_init_users_and_refresh_tokens.py


def downgrade() -> None:
    """Downgrade schema."""
    pass  # Nothing to drop; table is owned by 35d0060ebab4
