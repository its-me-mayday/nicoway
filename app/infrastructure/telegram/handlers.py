from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.application.services.deal_evaluator import DealEvaluator
from app.application.services.search_service import SearchService
from app.config import get_settings
from app.domain.models import TravelSearch
from app.infrastructure.db.repositories import (
    DealRepository,
    TravelSearchRepository,
    UserRepository,
)
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider
from app.infrastructure.telegram.keyboards import remove_keyboard

(
    SEARCH_NAME,
    ORIGIN,
    DESTINATION,
    DATE_FROM,
    DATE_TO,
    FLEXIBLE_DAYS,
    ADULTS,
    MAX_BUDGET,
    MAX_FLIGHT_PRICE,
    MAX_HOTEL_PRICE,
) = range(10)


def _chat_id(update: Update) -> int:
    if not update.effective_chat:
        raise ValueError("Missing Telegram chat")
    return update.effective_chat.id


def _username(update: Update) -> str | None:
    return update.effective_user.username if update.effective_user else None


def _parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value.replace(",", ".").strip())
    except InvalidOperation as exc:
        raise ValueError("Numero non valido") from exc


def _parse_date(value: str):
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with SessionLocal() as session:
        UserRepository(session).get_or_create(_chat_id(update), _username(update))
        session.commit()
    await update.message.reply_text(
        "Ciao, sono NicoWay. Tengo d'occhio voli e hotel per i vostri viaggi, "
        "e ti avviso quando spunta un deal che vale una piccola fuga insieme.\n\n"
        "Usa /newsearch per creare una ricerca o /help per vedere i comandi."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/newsearch - crea una nuova ricerca guidata\n"
        "/searches - mostra le ricerche\n"
        "/enable <id> - attiva una ricerca\n"
        "/disable <id> - disattiva una ricerca\n"
        "/delete <id> - elimina una ricerca\n"
        "/check <id> - controlla ora\n"
        "/best <id> - miglior deal trovato\n"
        "/settings - impostazioni base"
    )


async def newsearch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"] = {}
    await update.message.reply_text("Come vuoi chiamare questa ricerca? Esempio: Scozia 2026")
    return SEARCH_NAME


async def collect_search_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["name"] = update.message.text.strip()
    await update.message.reply_text("Aeroporto di partenza? Esempio: FCO")
    return ORIGIN


async def collect_origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["origin"] = update.message.text.strip().upper()
    await update.message.reply_text("Destinazione? Esempio: Edimburgo")
    return DESTINATION


async def collect_destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["destination"] = update.message.text.strip()
    await update.message.reply_text("Data inizio in formato YYYY-MM-DD")
    return DATE_FROM


async def collect_date_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["date_from"] = _parse_date(update.message.text)
    except ValueError:
        await update.message.reply_text("Formato data non valido. Usa YYYY-MM-DD.")
        return DATE_FROM
    await update.message.reply_text("Data fine in formato YYYY-MM-DD")
    return DATE_TO


async def collect_date_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["date_to"] = _parse_date(update.message.text)
    except ValueError:
        await update.message.reply_text("Formato data non valido. Usa YYYY-MM-DD.")
        return DATE_TO
    await update.message.reply_text("Flessibilità giorni? Esempio: 2")
    return FLEXIBLE_DAYS


async def collect_flexible_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["flexible_days"] = int(update.message.text.strip())
    await update.message.reply_text("Adulti? Esempio: 2")
    return ADULTS


async def collect_adults(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["adults"] = int(update.message.text.strip())
    await update.message.reply_text("Budget massimo totale? Esempio: 1800")
    return MAX_BUDGET


async def collect_max_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["max_budget_total"] = _parse_decimal(update.message.text)
    await update.message.reply_text("Prezzo massimo volo totale? Esempio: 350")
    return MAX_FLIGHT_PRICE


async def collect_max_flight_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["max_flight_price"] = _parse_decimal(update.message.text)
    await update.message.reply_text("Prezzo massimo hotel per notte? Esempio: 120")
    return MAX_HOTEL_PRICE


async def collect_max_hotel_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings = get_settings()
    data = context.user_data["new_search"]
    data["max_hotel_price_per_night"] = _parse_decimal(update.message.text)
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        row = TravelSearchRepository(session).add(
            TravelSearch(
                id=None,
                user_id=user.id,
                name=data["name"],
                origin=data["origin"],
                destination=data["destination"],
                date_from=data["date_from"],
                date_to=data["date_to"],
                flexible_days=data["flexible_days"],
                adults=data["adults"],
                children=0,
                max_budget_total=data["max_budget_total"],
                max_flight_price=data["max_flight_price"],
                max_hotel_price_per_night=data["max_hotel_price_per_night"],
                min_hotel_stars=3,
                preferred_departure_time_window="07-11",
                preferred_return_time_window="16-21",
                is_active=True,
                check_frequency_minutes=settings.default_check_frequency_minutes,
            )
        )
        session.commit()
    context.user_data.pop("new_search", None)
    await update.message.reply_text(
        f"Ricerca creata: {row.name} (id {row.id}). La tengo d'occhio.",
        reply_markup=remove_keyboard(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("new_search", None)
    await update.message.reply_text("Creazione annullata.", reply_markup=remove_keyboard())
    return ConversationHandler.END


async def searches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        rows = TravelSearchRepository(session).list_for_user(user.id)
    if not rows:
        await update.message.reply_text("Non ci sono ancora ricerche. Usa /newsearch.")
        return
    lines = [
        (
            f"{row.id}. {row.name} - {row.origin} → {row.destination} - "
            f"{'attiva' if row.is_active else 'pausa'}"
        )
        for row in rows
    ]
    await update.message.reply_text("\n".join(lines))


def _first_arg_int(context: ContextTypes.DEFAULT_TYPE) -> int | None:
    if not context.args:
        return None
    try:
        return int(context.args[0])
    except ValueError:
        return None


async def set_enabled(update: Update, context: ContextTypes.DEFAULT_TYPE, active: bool) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della ricerca.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        ok = TravelSearchRepository(session).set_active(search_id, user.id, active)
        session.commit()
    await update.message.reply_text("Fatto." if ok else "Ricerca non trovata.")


async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_enabled(update, context, True)


async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_enabled(update, context, False)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della ricerca.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        ok = TravelSearchRepository(session).delete(search_id, user.id)
        session.commit()
    await update.message.reply_text("Eliminata." if ok else "Ricerca non trovata.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della ricerca.")
        return
    settings = get_settings()
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        row = TravelSearchRepository(session).get_for_user(search_id, user.id)
        if not row:
            await update.message.reply_text("Ricerca non trovata.")
            return
        service = SearchService(
            session,
            MockFlightProvider(),
            MockHotelProvider(),
            DealEvaluator(settings),
            None,
        )
        candidate = await service.check_search(row, notify=False)
    if not candidate:
        await update.message.reply_text("Nessun deal compatibile trovato ora.")
        return
    await update.message.reply_text(
        f"Controllo fatto: totale {candidate.total_estimated_price:.0f} EUR, "
        f"score {candidate.score:.0f}/100."
    )


async def best(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della ricerca.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        row = TravelSearchRepository(session).get_for_user(search_id, user.id)
        if not row:
            await update.message.reply_text("Ricerca non trovata.")
            return
        deal = DealRepository(session).get_best_for_search(search_id)
        if not deal:
            await update.message.reply_text("Non ho ancora uno storico per questa ricerca.")
            return
        await update.message.reply_text(
            f"Miglior deal per {row.name}: {deal.total_estimated_price:.0f} EUR, "
            f"score {float(deal.score):.0f}/100."
        )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    await update.message.reply_text(
        f"Miglioramento prezzo minimo: {settings.min_price_improvement_percent:.0f}%\n"
        f"Miglioramento score minimo: {settings.min_score_improvement:.0f}\n"
        f"Cooldown notifiche: {settings.notification_cooldown_hours} ore\n"
        f"Frequenza default: {settings.default_check_frequency_minutes} minuti"
    )


def build_handlers():
    conversation = ConversationHandler(
        entry_points=[CommandHandler("newsearch", newsearch)],
        states={
            SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_search_name)],
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_origin)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_destination)],
            DATE_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_date_from)],
            DATE_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_date_to)],
            FLEXIBLE_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_flexible_days)],
            ADULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_adults)],
            MAX_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_max_budget)],
            MAX_FLIGHT_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_max_flight_price)
            ],
            MAX_HOTEL_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_max_hotel_price)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return [
        CommandHandler("start", start),
        CommandHandler("help", help_command),
        conversation,
        CommandHandler("searches", searches),
        CommandHandler("enable", enable),
        CommandHandler("disable", disable),
        CommandHandler("delete", delete),
        CommandHandler("check", check),
        CommandHandler("best", best),
        CommandHandler("settings", settings_command),
    ]
