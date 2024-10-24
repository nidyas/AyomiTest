"""init

Revision ID: 3b9121cf9297
Revises: 
Create Date: 2024-10-24 23:54:33.623791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b9121cf9297'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'operations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('expression', sa.String(), nullable=False),
        sa.Column('result', sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('operations')

