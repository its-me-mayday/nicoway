from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.application.services.deal_evaluator import DealEvaluator
from app.application.services.notification_service import NotificationService
from app.application.services.search_service import SearchService
from app.config import Settings
from app.infrastructure.db.repositories import NotificationRepository, TravelSearchRepository
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            lambda: asyncio.create_task(self.run_once()),
            "interval",
            minutes=1,
            id="active-searches-scan",
            replace_existing=True,
        )
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def run_once(self) -> None:
        with SessionLocal() as session:
            searches = TravelSearchRepository(session).list_active()
            for search in searches:
                try:
                    notification_service = NotificationService(
                        self.settings, NotificationRepository(session)
                    )
                    service = SearchService(
                        session=session,
                        flight_provider=MockFlightProvider(),
                        hotel_provider=MockHotelProvider(),
                        evaluator=DealEvaluator(self.settings),
                        notification_service=notification_service,
                    )
                    await service.check_search(search, notify=True)
                except Exception:
                    logger.exception("Search check failed", extra={"search_id": search.id})
