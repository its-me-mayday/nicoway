from decimal import Decimal

from app.application.services.deal_evaluator import DealEvaluator
from app.application.services.search_service import SearchService
from app.config import Settings
from app.infrastructure.db.repositories import DealRepository, TravelSearchRepository
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider


def test_create_travel_search(session, persisted_search):
    rows = TravelSearchRepository(session).list_all()

    assert len(rows) == 1
    assert rows[0].name == "Scozia 2026"
    assert persisted_search.max_budget_total == Decimal("350")
    assert persisted_search.max_stops == 0


async def test_manual_search_check_persists_snapshot(session, persisted_search):
    service = SearchService(
        session,
        MockFlightProvider(),
        DealEvaluator(Settings()),
        notification_service=None,
    )

    candidate = await service.check_search(persisted_search, notify=False)
    snapshots = DealRepository(session).list_for_search(persisted_search.id)

    assert candidate is not None
    assert len(snapshots) == 1
    assert snapshots[0].total_estimated_price == candidate.total_estimated_price
    assert candidate.flight is not None


async def test_max_stops_filter_blocks_connecting_flights(session, persisted_search):
    persisted_search.max_stops = 0  # solo diretti
    service = SearchService(
        session,
        MockFlightProvider(),
        DealEvaluator(Settings()),
        notification_service=None,
    )

    candidate = await service.check_search(persisted_search, notify=False)

    assert candidate is not None
    assert candidate.flight.stops == 0
