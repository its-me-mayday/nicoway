from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal

from app.domain.models import FlightOffer, TravelSearch
from app.infrastructure.providers.flights.base import FlightProvider


class MockFlightProvider(FlightProvider):
    name = "mock_flights"

    async def search(self, search: TravelSearch) -> list[FlightOffer]:
        base_date = search.date_from
        destination_code = search.destination[:3].upper()
        origin = search.origin.upper()
        offers: list[FlightOffer] = []
        templates = [
            (time(8, 20), time(11, 15), time(19, 10), time(22, 0), Decimal("142"), 0, 175),
            (time(6, 45), time(12, 30), time(17, 25), time(23, 10), Decimal("118"), 1, 345),
            (time(14, 10), time(17, 0), time(9, 35), time(12, 20), Decimal("189"), 0, 170),
        ]
        for idx, item in enumerate(templates):
            dep_t, arr_t, ret_dep_t, ret_arr_t, price, stops, duration = item
            outbound = datetime.combine(base_date + timedelta(days=idx % 2), dep_t)
            ret_date = search.date_to - timedelta(days=idx % 2)
            booking_url = f"https://example.com/flights/{origin}-{destination_code}-{idx + 1}"
            offers.append(
                FlightOffer(
                    id=None,
                    provider=self.name,
                    origin=origin,
                    destination=destination_code,
                    departure_datetime=outbound,
                    arrival_datetime=datetime.combine(outbound.date(), arr_t),
                    return_departure_datetime=datetime.combine(ret_date, ret_dep_t),
                    return_arrival_datetime=datetime.combine(ret_date, ret_arr_t),
                    total_price=price * search.adults,
                    currency="EUR",
                    stops=stops,
                    duration_minutes=duration,
                    booking_url=booking_url,
                    raw_payload={"mock_rank": idx + 1},
                )
            )
        return offers
