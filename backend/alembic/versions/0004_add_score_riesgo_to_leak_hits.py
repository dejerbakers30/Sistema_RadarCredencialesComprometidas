"""Add score_riesgo column to leak_hits table

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-11
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leak_hits", sa.Column("score_riesgo", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("leak_hits", "score_riesgo")

