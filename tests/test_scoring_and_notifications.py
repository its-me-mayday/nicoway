from decimal import Decimal

from app.application.services.deal_evaluator import DealEvaluator
from app.config import Settings
from app.domain.scoring import score_deal
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider


async def test_scoring_of_direct_flight(sample_search):
    flights = await MockFlightProvider().search(sample_search)
    direct = next(f for f in flights if f.stops == 0)

    score = score_deal(sample_search, direct, previous_best_price=Decimal("400"))

    assert 0 <= score <= 100


async def test_scoring_prefers_direct_over_stops(sample_search):
    flights = await MockFlightProvider().search(sample_search)
    direct = next(f for f in flights if f.stops == 0)
    with_stops = next(f for f in flights if f.stops > 0)

    score_direct = score_deal(sample_search, direct)
    score_stops = score_deal(sample_search, with_stops)

    assert score_direct > score_stops


async def test_deal_candidate_price_improvement(sample_search):
    flights = await MockFlightProvider().search(sample_search)
    evaluator = DealEvaluator(Settings())

    candidate = evaluator.build_candidate(sample_search, flights[0], Decimal("400"), 65)

    assert candidate.total_estimated_price == flights[0].total_price
    assert 0 <= candidate.score <= 100


async def test_should_notify_when_under_budget(sample_search):
    flights = await MockFlightProvider().search(sample_search)
    evaluator = DealEvaluator(Settings())

    candidate = evaluator.build_candidate(sample_search, flights[0], None, None)

    assert evaluator.should_notify(candidate)
