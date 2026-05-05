"""flights only: remove hotel tables/columns, add trip and max_stops

Revision ID: 0002_flights_only
Revises: 0001_initial
Create Date: 2026-05-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_flights_only"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "flight_trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_flight_trips_user_id", "flight_trips", ["user_id"])

    op.add_column(
        "travel_searches",
        sa.Column("max_stops", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "travel_searches",
        sa.Column(
            "trip_id",
            sa.Integer(),
            sa.ForeignKey("flight_trips.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_travel_searches_trip_id", "travel_searches", ["trip_id"])

    op.drop_column("travel_searches", "max_hotel_price_per_night")
    op.drop_column("travel_searches", "min_hotel_stars")

    op.alter_column("flight_offers", "return_departure_datetime", nullable=True)
    op.alter_column("flight_offers", "return_arrival_datetime", nullable=True)

    op.drop_constraint("deal_snapshots_hotel_offer_id_fkey", "deal_snapshots", type_="foreignkey")
    op.drop_column("deal_snapshots", "hotel_offer_id")

    op.drop_table("hotel_offers")


def downgrade() -> None:
    op.create_table(
        "hotel_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("hotel_name", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=128), nullable=False),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("checkout_date", sa.Date(), nullable=False),
        sa.Column("price_per_night", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Numeric(3, 1), nullable=False),
        sa.Column("booking_url", sa.Text(), nullable=False),
    )
    op.add_column("deal_snapshots", sa.Column("hotel_offer_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "deal_snapshots_hotel_offer_id_fkey",
        "deal_snapshots",
        "hotel_offers",
        ["hotel_offer_id"],
        ["id"],
    )
    op.add_column(
        "travel_searches",
        sa.Column("max_hotel_price_per_night", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column("travel_searches", sa.Column("min_hotel_stars", sa.Integer(), nullable=True))
    op.drop_index("ix_travel_searches_trip_id", "travel_searches")
    op.drop_column("travel_searches", "trip_id")
    op.drop_column("travel_searches", "max_stops")
    op.drop_index("ix_flight_trips_user_id", "flight_trips")
    op.drop_table("flight_trips")
