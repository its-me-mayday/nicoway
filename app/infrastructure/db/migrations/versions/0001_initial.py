"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-03
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_telegram_chat_id", "users", ["telegram_chat_id"], unique=True)

    op.create_table(
        "travel_searches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("origin", sa.String(length=32), nullable=False),
        sa.Column("destination", sa.String(length=128), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("flexible_days", sa.Integer(), nullable=False),
        sa.Column("adults", sa.Integer(), nullable=False),
        sa.Column("children", sa.Integer(), nullable=False),
        sa.Column("max_budget_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_flight_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_hotel_price_per_night", sa.Numeric(10, 2), nullable=True),
        sa.Column("min_hotel_stars", sa.Integer(), nullable=True),
        sa.Column("preferred_departure_time_window", sa.String(length=32), nullable=True),
        sa.Column("preferred_return_time_window", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("check_frequency_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_travel_searches_user_id", "travel_searches", ["user_id"])
    op.create_index("ix_travel_searches_is_active", "travel_searches", ["is_active"])

    op.create_table(
        "flight_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("origin", sa.String(length=32), nullable=False),
        sa.Column("destination", sa.String(length=128), nullable=False),
        sa.Column("departure_datetime", sa.DateTime(), nullable=False),
        sa.Column("arrival_datetime", sa.DateTime(), nullable=False),
        sa.Column("return_departure_datetime", sa.DateTime(), nullable=False),
        sa.Column("return_arrival_datetime", sa.DateTime(), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("stops", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("booking_url", sa.Text(), nullable=False),
        sa.Column(
            "raw_payload",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
    )

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
        sa.Column(
            "raw_payload",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
    )

    op.create_table(
        "deal_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "search_id",
            sa.Integer(),
            sa.ForeignKey("travel_searches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "flight_offer_id",
            sa.Integer(),
            sa.ForeignKey("flight_offers.id"),
            nullable=True,
        ),
        sa.Column("hotel_offer_id", sa.Integer(), sa.ForeignKey("hotel_offers.id"), nullable=True),
        sa.Column("total_estimated_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("is_notified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_deal_snapshots_created_at", "deal_snapshots", ["created_at"])

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "search_id",
            sa.Integer(),
            sa.ForeignKey("travel_searches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("notification_type", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_notification_logs_user_id", "notification_logs", ["user_id"])
    op.create_index("ix_notification_logs_sent_at", "notification_logs", ["sent_at"])


def downgrade() -> None:
    op.drop_table("notification_logs")
    op.drop_table("deal_snapshots")
    op.drop_table("hotel_offers")
    op.drop_table("flight_offers")
    op.drop_table("travel_searches")
    op.drop_table("users")
