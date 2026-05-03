from __future__ import annotations

from decimal import Decimal

from app.domain.models import HotelOffer, TravelSearch
from app.infrastructure.providers.hotels.base import HotelProvider


class MockHotelProvider(HotelProvider):
    name = "mock_hotels"

    async def search(self, search: TravelSearch) -> list[HotelOffer]:
        nights = max((search.date_to - search.date_from).days, 1)
        destination = search.destination.title()
        templates = [
            ("The Little Lantern Hotel", Decimal("86"), 4, 8.3),
            ("Nicole Garden Rooms", Decimal("72"), 3, 8.0),
            ("Harbor & Hearth Suites", Decimal("112"), 4, 9.0),
        ]
        offers: list[HotelOffer] = []
        for idx, (name, nightly, stars, rating) in enumerate(templates):
            if search.min_hotel_stars and stars < search.min_hotel_stars:
                continue
            destination_slug = destination.lower().replace(" ", "-")
            booking_url = f"https://example.com/hotels/{destination_slug}-{idx + 1}"
            offers.append(
                HotelOffer(
                    id=None,
                    provider=self.name,
                    hotel_name=name,
                    destination=destination,
                    checkin_date=search.date_from,
                    checkout_date=search.date_to,
                    price_per_night=nightly,
                    total_price=nightly * nights,
                    currency="EUR",
                    stars=stars,
                    rating=rating,
                    booking_url=booking_url,
                    raw_payload={"mock_rank": idx + 1, "nights": nights},
                )
            )
        return offers
