from app.infrastructure.providers.flights.mock_provider import MockFlightProvider


async def test_mock_flight_provider_returns_offers(sample_search):
    offers = await MockFlightProvider().search(sample_search)

    assert len(offers) == 4
    assert offers[0].origin == "FCO"
    assert offers[0].total_price > 0
    assert offers[0].booking_url.startswith("https://www.kayak.it/flights/")
    assert offers[0].return_departure_datetime is None


async def test_mock_flight_provider_direct_flights(sample_search):
    offers = await MockFlightProvider().search(sample_search)
    direct = [o for o in offers if o.stops == 0]
    assert len(direct) >= 2


async def test_mock_flight_provider_prices_scale_with_adults(sample_search):
    sample_search.adults = 1
    offers_1 = await MockFlightProvider().search(sample_search)
    sample_search.adults = 2
    offers_2 = await MockFlightProvider().search(sample_search)
    assert offers_2[0].total_price == offers_1[0].total_price * 2
