from __future__ import annotations

from decimal import Decimal

from telegram import Bot

from app.application.services.deal_evaluator import DealCandidate
from app.config import Settings
from app.infrastructure.db.repositories import NotificationRepository


def eur(value: Decimal) -> str:
    return f"{value:,.0f} EUR".replace(",", ".")


class NotificationService:
    def __init__(
        self,
        settings: Settings,
        notification_repository: NotificationRepository,
        bot: Bot | None = None,
    ) -> None:
        self.settings = settings
        self.notification_repository = notification_repository
        self.bot = (
            bot
            if bot
            else Bot(settings.telegram_bot_token)
            if settings.telegram_bot_token
            else None
        )

    def render_deal_message(self, candidate: DealCandidate) -> str:
        flight = candidate.flight
        hotel = candidate.hotel
        improvement = candidate.price_improvement_percent
        improvement_line = (
            f"📉 Miglioramento: -{abs(improvement):.0f}% rispetto al miglior prezzo precedente"
            if improvement > 0
            else "📉 Primo buon riferimento salvato per questa ricerca"
        )
        return (
            f"🚀 Nuovo deal trovato per {candidate.search.name}!\n\n"
            "✈️ Volo:\n"
            f"{flight.origin} → {flight.destination}\n"
            f"Partenza: {flight.departure_datetime:%d/%m/%Y %H:%M}\n"
            f"Ritorno: {flight.return_departure_datetime:%d/%m/%Y %H:%M}\n"
            f"Prezzo: {eur(flight.total_price)}\n"
            f"Scali: {flight.stops}\n\n"
            "🏨 Hotel:\n"
            f"{hotel.hotel_name}\n"
            f"Prezzo medio/notte: {eur(hotel.price_per_night)}\n"
            f"Totale stimato hotel: {eur(hotel.total_price)}\n"
            f"Rating medio: {hotel.rating:.1f}\n\n"
            f"💰 Totale stimato: {eur(candidate.total_estimated_price)}\n"
            f"{improvement_line}\n"
            f"⭐ Score: {candidate.score:.0f}/100\n\n"
            f"🔗 Prenota volo: {flight.booking_url}\n"
            f"🔗 Cerca hotel: {hotel.booking_url}\n\n"
            "Sembra una piccola finestra buona per voi due."
        )

    async def send_deal(self, chat_id: int, user_id: int, candidate: DealCandidate) -> bool:
        message = self.render_deal_message(candidate)
        if self.notification_repository.has_recent_identical(
            user_id,
            candidate.search.id or 0,
            message,
            self.settings.notification_cooldown_hours,
        ):
            return False
        if self.bot:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                disable_web_page_preview=True,
            )
        self.notification_repository.add(user_id, candidate.search.id or 0, message, "deal")
        return True
