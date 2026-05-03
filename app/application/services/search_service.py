from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.services.deal_evaluator import DealCandidate, DealEvaluator
from app.application.services.notification_service import NotificationService
from app.domain.models import TravelSearch
from app.infrastructure.db.repositories import DealRepository, search_to_domain
from app.infrastructure.providers.flights.base import FlightProvider
from app.infrastructure.providers.hotels.base import HotelProvider


class SearchService:
    def __init__(
        self,
        session: Session,
        flight_provider: FlightProvider,
        hotel_provider: HotelProvider,
        evaluator: DealEvaluator,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.session = session
        self.deals = DealRepository(session)
        self.flight_provider = flight_provider
        self.hotel_provider = hotel_provider
        self.evaluator = evaluator
        self.notification_service = notification_service

    async def check_search(self, search_orm, notify: bool = True) -> DealCandidate | None:
        search: TravelSearch = search_to_domain(search_orm)
        previous_best = self.deals.get_best_for_search(search.id or 0)
        previous_best_price = previous_best.total_estimated_price if previous_best else None
        previous_best_score = float(previous_best.score) if previous_best else None

        flights = await self.flight_provider.search(search)
        hotels = await self.hotel_provider.search(search)
        if search.max_flight_price is not None:
            flights = [
                flight for flight in flights if flight.total_price <= search.max_flight_price
            ]
        if search.max_hotel_price_per_night is not None:
            hotels = [
                hotel
                for hotel in hotels
                if hotel.price_per_night <= search.max_hotel_price_per_night
            ]
        if not flights or not hotels:
            return None

        candidates = [
            self.evaluator.build_candidate(
                search,
                flight,
                hotel,
                previous_best_price,
                previous_best_score,
            )
            for flight in flights
            for hotel in hotels
        ]
        best = max(
            candidates,
            key=lambda candidate: (candidate.score, -candidate.total_estimated_price),
        )

        flight_row = self.deals.save_flight(best.flight)
        hotel_row = self.deals.save_hotel(best.hotel)
        snapshot = self.deals.save_snapshot(
            search_id=search.id or 0,
            flight_offer_id=flight_row.id,
            hotel_offer_id=hotel_row.id,
            total_estimated_price=best.total_estimated_price,
            score=best.score,
        )
        self.session.flush()

        if notify and self.notification_service and self.evaluator.should_notify(best):
            sent = await self.notification_service.send_deal(
                chat_id=search_orm.user.telegram_chat_id,
                user_id=search.user_id,
                candidate=best,
            )
            if sent:
                self.deals.mark_notified(snapshot.id)
        self.session.commit()
        return best
