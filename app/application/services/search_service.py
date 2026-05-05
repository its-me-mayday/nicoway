from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.application.services.deal_evaluator import DealCandidate, DealEvaluator
from app.application.services.notification_service import NotificationService
from app.domain.models import TravelSearch
from app.infrastructure.db.repositories import DealRepository, search_to_domain
from app.infrastructure.providers.flights.base import FlightProvider

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        session: Session,
        flight_provider: FlightProvider,
        evaluator: DealEvaluator,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.session = session
        self.deals = DealRepository(session)
        self.flight_provider = flight_provider
        self.evaluator = evaluator
        self.notification_service = notification_service

    async def check_search(self, search_orm, notify: bool = True) -> DealCandidate | None:
        search: TravelSearch = search_to_domain(search_orm)
        logger.info("🔍 Check %s → %s  [%s]", search.origin, search.destination, search.name)

        previous_best = self.deals.get_best_for_search(search.id or 0)
        previous_best_price = previous_best.total_estimated_price if previous_best else None
        previous_best_score = float(previous_best.score) if previous_best else None

        flights = await self.flight_provider.search(search)
        logger.info("   Trovati %d voli da %s", len(flights), self.flight_provider.name)

        pre_stops = len(flights)
        if search.max_stops >= 0:
            flights = [f for f in flights if f.stops <= search.max_stops]
        if pre_stops != len(flights):
            logger.info("   ✗ Filtro scali (max %d): %d→%d voli rimasti", search.max_stops, pre_stops, len(flights))

        pre_price = len(flights)
        if search.max_flight_price is not None:
            flights = [f for f in flights if f.total_price <= search.max_flight_price]
        if pre_price != len(flights):
            logger.info("   ✗ Filtro prezzo volo (max €%.0f): %d→%d voli rimasti", search.max_flight_price, pre_price, len(flights))

        if not flights:
            logger.info("   ❌ Nessun volo dopo i filtri (scali/prezzo)")
            return None

        candidates = [
            self.evaluator.build_candidate(search, flight, previous_best_price, previous_best_score)
            for flight in flights
        ]
        best = max(candidates, key=lambda c: (c.score, -c.total_estimated_price))
        logger.info(
            "   Migliore: %s %s  €%.0f  score %.0f  %s scal%s",
            best.flight.airline or "—",
            best.flight.departure_datetime.strftime("%d/%m %H:%M"),
            best.total_estimated_price,
            best.score,
            best.flight.stops,
            "o" if best.flight.stops == 1 else "i",
        )

        is_improvement = (
            previous_best_price is None
            or best.total_estimated_price < previous_best_price
        )
        if not is_improvement:
            logger.info(
                "   Prezzo invariato (prec. €%.0f) — snapshot non salvato", previous_best_price
            )
            self.session.commit()
            return best

        flight_row = self.deals.save_flight(best.flight)
        snapshot = self.deals.save_snapshot(
            search_id=search.id or 0,
            flight_offer_id=flight_row.id,
            total_estimated_price=best.total_estimated_price,
            score=best.score,
        )
        self.session.flush()
        logger.info("   💾 Offerta salvata (id=%s)", snapshot.id)

        if notify and self.notification_service and self.evaluator.should_notify(best):
            sent = await self.notification_service.send_deal(
                chat_id=search_orm.user.telegram_chat_id,
                user_id=search.user_id,
                candidate=best,
            )
            if sent:
                self.deals.mark_notified(snapshot.id)
                logger.info("   📨 Notifica Telegram inviata")
            else:
                logger.info("   📨 Notifica non inviata (cooldown o duplicato)")

        self.session.commit()
        return best
