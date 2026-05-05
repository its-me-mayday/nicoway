from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


json_type = JSON().with_variant(JSONB, "postgresql")


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    searches: Mapped[list[TravelSearchORM]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    trips: Mapped[list[FlightTripORM]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class FlightTripORM(Base):
    __tablename__ = "flight_trips"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[UserORM] = relationship(back_populates="trips")
    searches: Mapped[list[TravelSearchORM]] = relationship(back_populates="trip")


class TravelSearchORM(Base):
    __tablename__ = "travel_searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    trip_id: Mapped[int | None] = mapped_column(
        ForeignKey("flight_trips.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    origin: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(128))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    flexible_days: Mapped[int] = mapped_column(Integer, default=0)
    adults: Mapped[int] = mapped_column(Integer, default=2)
    children: Mapped[int] = mapped_column(Integer, default=0)
    max_budget_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    max_flight_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_stops: Mapped[int] = mapped_column(Integer, default=0)
    preferred_departure_time_window: Mapped[str | None] = mapped_column(String(32), nullable=True)
    preferred_return_time_window: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    check_frequency_minutes: Mapped[int] = mapped_column(Integer, default=180)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped[UserORM] = relationship(back_populates="searches")
    trip: Mapped[FlightTripORM | None] = relationship(back_populates="searches")
    snapshots: Mapped[list[DealSnapshotORM]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class FlightOfferORM(Base):
    __tablename__ = "flight_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(100))
    origin: Mapped[str] = mapped_column(String(32))
    destination: Mapped[str] = mapped_column(String(128))
    departure_datetime: Mapped[datetime] = mapped_column(DateTime)
    arrival_datetime: Mapped[datetime] = mapped_column(DateTime)
    return_departure_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    return_arrival_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    stops: Mapped[int] = mapped_column(Integer, default=0)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    booking_url: Mapped[str] = mapped_column(Text)
    airline: Mapped[str | None] = mapped_column(String(10), nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)


class DealSnapshotORM(Base):
    __tablename__ = "deal_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[int] = mapped_column(ForeignKey("travel_searches.id", ondelete="CASCADE"))
    flight_offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("flight_offers.id"), nullable=True
    )
    total_estimated_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    score: Mapped[float] = mapped_column(Numeric(5, 2))
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    search: Mapped[TravelSearchORM] = relationship(back_populates="snapshots")
    flight_offer: Mapped[FlightOfferORM | None] = relationship()


class NotificationLogORM(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    search_id: Mapped[int] = mapped_column(ForeignKey("travel_searches.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    notification_type: Mapped[str] = mapped_column(String(64))
