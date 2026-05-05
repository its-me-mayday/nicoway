from __future__ import annotations

import logging
from datetime import date as date_type, datetime, timedelta
from decimal import Decimal

import httpx

from app.domain.models import FlightOffer, TravelSearch
from app.infrastructure.providers.flights.base import FlightProvider

logger = logging.getLogger(__name__)

_CHEAP_URL = "https://api.travelpayouts.com/v1/prices/cheap"

# Rough duration estimates (minutes) when the API doesn't provide them.
# Keyed by (stops): nonstop, 1 stop, 2+ stops.
_DURATION_BY_STOPS = {0: 150, 1: 280, 2: 420}


def _estimate_duration(stops: int) -> int:
    return _DURATION_BY_STOPS.get(stops, _DURATION_BY_STOPS[2])


def _booking_url(origin: str, destination: str, dep_dt: datetime, adults: int) -> str:
    return (
        f"https://www.aviasales.com/search/"
        f"{origin}{dep_dt.strftime('%d%m')}{destination}{adults}"
    )


class TravelpayoutsFlightProvider(FlightProvider):
    name = "travelpayouts"

    def __init__(self, token: str) -> None:
        self.token = token

    async def search(self, search: TravelSearch) -> list[FlightOffer]:
        origin = search.origin[:3].upper()
        destination = search.destination[:3].upper()

        # Travelpayouts cheap API only supports YYYY-MM granularity.
        depart_date = search.date_from.strftime("%Y-%m")

        params = {
            "origin": origin,
            "destination": destination,
            "depart_date": depart_date,
            "currency": "eur",
            "token": self.token,
            "one_way": "true",
        }

        # For single-day searches (trip legs), allow ±7 days so the API's monthly cheapest can match.
        flex = max(search.flexible_days, 7 if search.date_from == search.date_to else 0)
        date_min = search.date_from - timedelta(days=flex)
        date_max = search.date_to + timedelta(days=flex)
        logger.info("   → Travelpayouts: %s→%s  data=%s  finestra=%s..%s",
                    origin, destination, depart_date, date_min, date_max)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(_CHEAP_URL, params=params)
                r.raise_for_status()
                payload = r.json()
        except Exception:
            logger.exception("Travelpayouts API call failed for %s→%s", origin, destination)
            return []

        if not payload.get("success"):
            logger.warning("Travelpayouts returned success=false: %s", payload)
            return []

        offers: list[FlightOffer] = []
        for _dest_key, flights_by_stops in payload.get("data", {}).items():
            for stops_str, flight in flights_by_stops.items():
                try:
                    stops = int(stops_str)
                    dep_dt = datetime.fromisoformat(flight["departure_at"])

                    if not (date_min <= dep_dt.date() <= date_max):
                        continue
                    if not (date_min <= dep_dt.date() <= date_max):
                        logger.debug("   ✗ scartato %s (fuori finestra %s..%s)", dep_dt.date(), date_min, date_max)
                        continue

                    duration = int(flight.get("duration_to") or _estimate_duration(stops))
                    arr_dt = dep_dt + timedelta(minutes=duration)
                    price_pp = Decimal(str(flight["price"]))
                    airline = flight.get("airline") or ""

                    offers.append(
                        FlightOffer(
                            id=None,
                            provider=self.name,
                            origin=origin,
                            destination=destination,
                            departure_datetime=dep_dt,
                            arrival_datetime=arr_dt,
                            return_departure_datetime=None,
                            return_arrival_datetime=None,
                            total_price=price_pp * search.adults,
                            currency=payload.get("currency", "eur").upper(),
                            stops=stops,
                            duration_minutes=duration,
                            booking_url=_booking_url(origin, destination, dep_dt, search.adults),
                            airline=airline,
                            raw_payload=flight,
                        )
                    )
                except Exception:
                    logger.exception("Failed to parse flight offer: %s", flight)

        return offers
