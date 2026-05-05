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
        improvement = candidate.price_improvement_percent
        improvement_line = (
            f"📉 -{abs(improvement):.0f}% rispetto al miglior prezzo precedente"
            if improvement > 0
            else "📌 Primo prezzo di riferimento salvato"
        )
        stops_label = (
            "diretto" if flight.stops == 0
            else f"{flight.stops} scal{'o' if flight.stops == 1 else 'i'}"
        )
        lines = [
            f"✈️ Volo trovato per {candidate.search.name}!",
            "",
            f"{flight.origin} → {flight.destination}",
            f"Partenza: {flight.departure_datetime:%d/%m/%Y %H:%M}",
            f"Arrivo: {flight.arrival_datetime:%d/%m/%Y %H:%M}",
        ]
        if flight.return_departure_datetime:
            lines += [
                f"Ritorno: {flight.return_departure_datetime:%d/%m/%Y %H:%M}",
            ]
        lines += [
            f"Prezzo: {eur(flight.total_price)} · {stops_label}",
            f"Durata: {flight.duration_minutes // 60}h{flight.duration_minutes % 60:02d}m",
            "",
            f"💰 {eur(candidate.total_estimated_price)}",
            improvement_line,
            f"⭐ Score: {candidate.score:.0f}/100",
            "",
            f"🔗 {flight.booking_url}",
        ]
        return "\n".join(lines)

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
