from decimal import Decimal

from app.application.services.deal_evaluator import DealEvaluator
from app.config import Settings
from app.domain.scoring import score_deal
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider


async def test_scoring_of_deal(sample_search):
    flight = (await MockFlightProvider().search(sample_search))[0]
    hotel = (await MockHotelProvider().search(sample_search))[0]

    score = score_deal(sample_search, flight, hotel, previous_best_price=Decimal("1700"))

    assert 0 <= score <= 100
    assert score > 60


async def test_deal_improvement_against_previous_best(sample_search):
    flight = (await MockFlightProvider().search(sample_search))[0]
    hotel = (await MockHotelProvider().search(sample_search))[0]
    evaluator = DealEvaluator(Settings())

    candidate = evaluator.build_candidate(sample_search, flight, hotel, Decimal("1700"), 65)

    assert candidate.price_improvement_percent > 10
    assert candidate.score_improvement >= 0


async def test_notification_decision(sample_search):
    flight = (await MockFlightProvider().search(sample_search))[0]
    hotel = (await MockHotelProvider().search(sample_search))[0]
    evaluator = DealEvaluator(Settings())

    candidate = evaluator.build_candidate(sample_search, flight, hotel, Decimal("1700"), 60)

    assert evaluator.should_notify(candidate)
