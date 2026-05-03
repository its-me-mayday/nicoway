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
    max_hotel_price_per_night: Decimal | None
    min_hotel_stars: int | None
    preferred_departure_time_window: str | None
    preferred_return_time_window: str | None
    is_active: bool
    check_frequency_minutes: int
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
    return_departure_datetime: datetime
    return_arrival_datetime: datetime
    total_price: Decimal
    currency: str
    stops: int
    duration_minutes: int
    booking_url: str
    raw_payload: dict[str, Any] | None = None


@dataclass(slots=True)
class HotelOffer:
    id: int | None
    provider: str
    hotel_name: str
    destination: str
    checkin_date: date
    checkout_date: date
    price_per_night: Decimal
    total_price: Decimal
    currency: str
    stars: int
    rating: float
    booking_url: str
    raw_payload: dict[str, Any] | None = None


@dataclass(slots=True)
class DealSnapshot:
    id: int | None
    search_id: int
    flight_offer_id: int | None
    hotel_offer_id: int | None
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
