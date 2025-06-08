"""Add status column to Knowledge Base table

Revision ID: c2b651c25200
Revises: faafd4ce8f16
Create Date: 2025-06-08 23:48:56.200178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2b651c25200'
down_revision: Union[str, None] = 'faafd4ce8f16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('knowledge_bases', sa.Column('status', sa.String(length=50), autoincrement=False, nullable=True))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('knowledge_bases', 'status')
    pass
