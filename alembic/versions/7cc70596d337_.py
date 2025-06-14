"""empty message

Revision ID: 7cc70596d337
Revises: d25179e5825d
Create Date: 2025-06-02 00:30:33.700897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cc70596d337'
down_revision: Union[str, None] = 'd25179e5825d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('videos', 'views',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('videos', 'likes',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('videos', 'dislikes',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('videos', 'dislikes',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('videos', 'likes',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('videos', 'views',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
