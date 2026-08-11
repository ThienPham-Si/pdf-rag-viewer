"""Migrate to 768 embeddings

Revision ID: f612ab7c33d2
Revises: 434a4534dd46
Create Date: 2026-08-11 15:12:29.220455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

# revision identifiers, used by Alembic.
revision: str = 'f612ab7c33d2'
down_revision: Union[str, Sequence[str], None] = '434a4534dd46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing 1536-dim embeddings and add 768-dim embeddings
    op.drop_column('chunks', 'embedding')
    op.add_column('chunks', sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True))


def downgrade() -> None:
    # Revert to 1536-dim embeddings
    op.drop_column('chunks', 'embedding')
    op.add_column('chunks', sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True))
