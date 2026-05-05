from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class User:
    id: int | None
    telegram_chat_id: int
    username: str | None
    created_at: datetime | None = None


@dataclass(slots=True)
class FlightTrip:
    id: int | None
    user_id: int
    name: str
    created_at: datetime | None = None


@dataclass(slots=True)
class TravelSearch:
    id: int | None
    user_id: int
    name: str
    origin: str
    destination: str
    date_from: date
    date_to: date
    flexible_days: int
    adults: int
    children: int
    max_budget_total: Decimal
    max_flight_price: Decimal | None
    max_stops: int  # 0=diretto, -1=qualsiasi, N=max N scali
    preferred_departure_time_window: str | None
    preferred_return_time_window: str | None
    is_active: bool
    check_frequency_minutes: int
    trip_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class FlightOffer:
    id: int | None
    provider: str
    origin: str
    destination: str
    departure_datetime: datetime
    arrival_datetime: datetime
    return_departure_datetime: datetime | None
    return_arrival_datetime: datetime | None
    total_price: Decimal
    currency: str
    stops: int
    duration_minutes: int
    booking_url: str
    airline: str | None = None
    raw_payload: dict[str, Any] | None = None


@dataclass(slots=True)
class DealSnapshot:
    id: int | None
    search_id: int
    flight_offer_id: int | None
    total_estimated_price: Decimal
    score: float
    is_notified: bool
    created_at: datetime | None = None


@dataclass(slots=True)
class NotificationLog:
    id: int | None
    user_id: int
    search_id: int
    message: str
    notification_type: str
    sent_at: datetime | None = None
