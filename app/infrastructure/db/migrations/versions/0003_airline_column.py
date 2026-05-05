"""add airline column to flight_offers

Revision ID: 0003_airline_column
Revises: 0002_flights_only
Create Date: 2026-05-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_airline_column"
down_revision = "0002_flights_only"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "flight_offers",
        sa.Column("airline", sa.String(length=10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("flight_offers", "airline")
