from __future__ import annotations

import hashlib
from datetime import datetime, time, timedelta
from decimal import Decimal

from app.domain.models import FlightOffer, TravelSearch
from app.infrastructure.providers.flights.base import FlightProvider


def _route_factor(origin: str, destination: str) -> float:
    """Deterministic price multiplier per route (0.5x – 2.5x base price)."""
    digest = hashlib.md5(f"{origin}{destination}".encode()).digest()
    return 0.5 + (digest[0] / 255) * 2.0


class MockFlightProvider(FlightProvider):
    name = "mock_flights"

    async def search(self, search: TravelSearch) -> list[FlightOffer]:
        base_date = search.date_from
        destination_code = search.destination[:3].upper()
        origin = search.origin.upper()
        factor = Decimal(str(round(_route_factor(origin, destination_code), 2)))

        templates = [
            (time(8, 20),  time(11, 15), Decimal("142"), 0, 175, "FR"),
            (time(6, 45),  time(12, 30), Decimal("118"), 1, 345, "U2"),
            (time(14, 10), time(17, 0),  Decimal("189"), 0, 170, "AZ"),
            (time(7, 0),   time(9, 45),  Decimal("205"), 2, 420, "W6"),
        ]
        offers: list[FlightOffer] = []
        for idx, (dep_t, arr_t, base_price, stops, duration, airline) in enumerate(templates):
            outbound = datetime.combine(base_date + timedelta(days=idx % 2), dep_t)
            price = (base_price * factor).quantize(Decimal("1"))
            booking_url = (
                f"https://www.kayak.it/flights/{origin}-{destination_code}"
                f"/{outbound.strftime('%Y-%m-%d')}/{search.adults}adults"
            )
            offers.append(
                FlightOffer(
                    id=None,
                    provider=self.name,
                    origin=origin,
                    destination=destination_code,
                    departure_datetime=outbound,
                    arrival_datetime=datetime.combine(outbound.date(), arr_t),
                    return_departure_datetime=None,
                    return_arrival_datetime=None,
                    total_price=price * search.adults,
                    currency="EUR",
                    stops=stops,
                    duration_minutes=duration,
                    booking_url=booking_url,
                    airline=airline,
                    raw_payload={"mock_rank": idx + 1},
                )
            )
        return offers
