from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.domain.models import FlightOffer, TravelSearch


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def _parse_hour_window(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    try:
        start, end = value.split("-", maxsplit=1)
        return int(start[:2]), int(end[:2])
    except (ValueError, TypeError):
        return None


def _time_window_score(moment: datetime, configured: str | None) -> float:
    window = _parse_hour_window(configured)
    if window is None:
        return 70
    start, end = window
    hour = moment.hour
    inside = start <= hour <= end if start <= end else hour >= start or hour <= end
    return 100 if inside else 45


def score_deal(
    search: TravelSearch,
    flight: FlightOffer,
    previous_best_price: Decimal | None = None,
) -> float:
    total = flight.total_price
    budget = search.max_budget_total
    price_ratio_score = _clamp(100 - (float(total / budget) * 80)) if budget > 0 else 50

    flight_cap = search.max_flight_price or max(flight.total_price, Decimal("1"))
    flight_price_score = _clamp(100 - float(flight.total_price / flight_cap) * 60)

    stops_score = _clamp(100 - flight.stops * 30)
    duration_score = _clamp(100 - max(flight.duration_minutes - 90, 0) / 5)
    departure_score = _time_window_score(
        flight.departure_datetime, search.preferred_departure_time_window
    )

    return_score = 70.0
    if flight.return_departure_datetime:
        return_score = _time_window_score(
            flight.return_departure_datetime, search.preferred_return_time_window
        )

    improvement_score = 50.0
    if previous_best_price and total < previous_best_price:
        improvement = float((previous_best_price - total) / previous_best_price) * 100
        improvement_score = _clamp(55 + improvement * 1.5)

    score = (
        price_ratio_score * 0.30
        + flight_price_score * 0.20
        + stops_score * 0.20
        + duration_score * 0.12
        + departure_score * 0.10
        + return_score * 0.05
        + improvement_score * 0.03
    )
    return round(_clamp(score), 2)
