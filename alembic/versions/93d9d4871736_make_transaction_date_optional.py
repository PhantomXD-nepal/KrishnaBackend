"""Make transaction date optional

Revision ID: 93d9d4871736
Revises: c9cab290f043
Create Date: 2025-08-09 14:24:47.037565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93d9d4871736'
down_revision: Union[str, Sequence[str], None] = 'c9cab290f043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('date_created', existing_type=sa.DATETIME(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('date_created', existing_type=sa.DATETIME(), nullable=False)
