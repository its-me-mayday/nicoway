from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider


async def test_mock_flight_provider_returns_realistic_offers(sample_search):
    offers = await MockFlightProvider().search(sample_search)

    assert len(offers) == 3
    assert offers[0].origin == "FCO"
    assert offers[0].total_price > 0
    assert offers[0].booking_url.startswith("https://example.com/flights/")


async def test_mock_hotel_provider_returns_realistic_offers(sample_search):
    offers = await MockHotelProvider().search(sample_search)

    assert len(offers) == 3
    assert offers[0].destination == "Edimburgo"
    assert offers[0].total_price > offers[0].price_per_night
    assert offers[0].rating >= 8
