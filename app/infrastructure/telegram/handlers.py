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
    FlightTripRepository,
    TravelSearchRepository,
    UserRepository,
)
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.telegram.keyboards import remove_keyboard

(
    SEARCH_NAME,
    ORIGIN,
    DESTINATION,
    DATE_FROM,
    DATE_TO,
    FLEXIBLE_DAYS,
    ADULTS,
    MAX_STOPS,
    MAX_FLIGHT_PRICE,
    TRIP_NAME,
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
    chat_id = _chat_id(update)
    with SessionLocal() as session:
        UserRepository(session).get_or_create(chat_id, _username(update))
        session.commit()
    await update.message.reply_text(
        "Ciao, sono NicoWay. Monitoro voli per i tuoi viaggi e ti avviso quando trovo "
        "un'offerta sotto il tuo budget.\n\n"
        f"Il tuo chat id: {chat_id}\n\n"
        "Usa /newsearch per monitorare una tratta o /newtrip per un viaggio multi-tratta.\n"
        "Scrivi /help per tutti i comandi."
    )


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = _chat_id(update)
    with SessionLocal() as session:
        UserRepository(session).get_or_create(chat_id, _username(update))
        session.commit()
    await update.message.reply_text(f"Il tuo chat id: {chat_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/chatid - mostra il tuo chat id\n"
        "/newsearch - monitora una nuova tratta volo\n"
        "/newtrip - crea un viaggio con più tratte\n"
        "/searches - lista tratte attive\n"
        "/trips - lista viaggi\n"
        "/enable <id> - attiva una tratta\n"
        "/disable <id> - metti in pausa una tratta\n"
        "/delete <id> - elimina una tratta\n"
        "/check <id> - controlla subito una tratta\n"
        "/best <id> - miglior volo trovato\n"
        "/settings - impostazioni"
    )


# ── /newsearch conversation ────────────────────────────────────────────────────

async def newsearch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"] = {}
    await update.message.reply_text(
        "Come vuoi chiamare questa tratta? Es: Roma - Londra Agosto 2026"
    )
    return SEARCH_NAME


async def collect_search_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["name"] = update.message.text.strip()
    await update.message.reply_text("Aeroporto di partenza (codice IATA)? Es: FCO")
    return ORIGIN


async def collect_origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["origin"] = update.message.text.strip().upper()
    await update.message.reply_text("Aeroporto di arrivo (codice IATA)? Es: LHR")
    return DESTINATION


async def collect_destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_search"]["destination"] = update.message.text.strip().upper()
    await update.message.reply_text("Data di partenza? Formato YYYY-MM-DD")
    return DATE_FROM


async def collect_date_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["date_from"] = _parse_date(update.message.text)
    except ValueError:
        await update.message.reply_text("Formato non valido. Usa YYYY-MM-DD.")
        return DATE_FROM
    await update.message.reply_text(
        "Data di fine finestra (per ricerche flessibili) in YYYY-MM-DD.\n"
        "Se non sei flessibile usa la stessa data di partenza."
    )
    return DATE_TO


async def collect_date_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["date_to"] = _parse_date(update.message.text)
    except ValueError:
        await update.message.reply_text("Formato non valido. Usa YYYY-MM-DD.")
        return DATE_TO
    await update.message.reply_text("Quanti giorni di flessibilità vuoi? Es: 0 (nessuna), 2, 3")
    return FLEXIBLE_DAYS


async def collect_flexible_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["flexible_days"] = max(0, int(update.message.text.strip()))
    except ValueError:
        context.user_data["new_search"]["flexible_days"] = 0
    await update.message.reply_text("Quanti adulti? Es: 2")
    return ADULTS


async def collect_adults(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["new_search"]["adults"] = max(1, int(update.message.text.strip()))
    except ValueError:
        context.user_data["new_search"]["adults"] = 1
    await update.message.reply_text(
        "Scali accettati?\n"
        "0 - solo voli diretti (default)\n"
        "1 - max 1 scalo\n"
        "2 - max 2 scali\n"
        "-1 - qualsiasi"
    )
    return MAX_STOPS


async def collect_max_stops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        val = int(update.message.text.strip())
        context.user_data["new_search"]["max_stops"] = max(-1, val)
    except ValueError:
        context.user_data["new_search"]["max_stops"] = 0
    await update.message.reply_text(
        "Prezzo massimo volo totale in EUR? Es: 350\n"
        "Scrivi 0 per nessun limite."
    )
    return MAX_FLIGHT_PRICE


async def collect_max_flight_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings = get_settings()
    data = context.user_data["new_search"]
    try:
        val = _parse_decimal(update.message.text)
        data["max_flight_price"] = val if val > 0 else None
    except ValueError:
        data["max_flight_price"] = None

    # max_budget_total = max_flight_price if set, else 9999 (no limit)
    data["max_budget_total"] = data["max_flight_price"] or Decimal("9999")

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
                max_stops=data["max_stops"],
                preferred_departure_time_window="07-11",
                preferred_return_time_window="16-21",
                is_active=True,
                check_frequency_minutes=settings.default_check_frequency_minutes,
            )
        )
        session.commit()
    context.user_data.pop("new_search", None)
    stops_label = (
        "diretto" if data["max_stops"] == 0
        else "qualsiasi scalo" if data["max_stops"] == -1
        else f"max {data['max_stops']} scal{'o' if data['max_stops']==1 else 'i'}"
    )
    await update.message.reply_text(
        f"Tratta creata: {row.name} (id {row.id})\n"
        f"{data['origin']} → {data['destination']} · {stops_label}\n"
        "La tengo d'occhio e ti avviso quando trovo qualcosa.",
        reply_markup=remove_keyboard(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("new_search", None)
    context.user_data.pop("new_trip", None)
    await update.message.reply_text("Operazione annullata.", reply_markup=remove_keyboard())
    return ConversationHandler.END


# ── /newtrip conversation ──────────────────────────────────────────────────────

async def newtrip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_trip"] = {}
    await update.message.reply_text("Come vuoi chiamare questo viaggio? Es: Scozia 2026")
    return TRIP_NAME


async def collect_trip_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        trip = FlightTripRepository(session).add(user.id, update.message.text.strip())
        session.commit()
        trip_id = trip.id
        trip_name = trip.name
    context.user_data.pop("new_trip", None)
    await update.message.reply_text(
        f"Viaggio \"{trip_name}\" creato con id {trip_id}.\n\n"
        "Ora aggiungi le tratte con /newsearch e associale a questo viaggio "
        f"inserendo l'id {trip_id} quando richiesto (dalla dashboard web o dall'API).\n\n"
        "Prossimamente aggiungerò la possibilità di farlo direttamente qui.",
        reply_markup=remove_keyboard(),
    )
    return ConversationHandler.END


# ── List commands ──────────────────────────────────────────────────────────────

async def searches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        rows = TravelSearchRepository(session).list_for_user(user.id)
    if not rows:
        await update.message.reply_text("Nessuna tratta. Usa /newsearch per crearla.")
        return
    lines = []
    for row in rows:
        if row.max_stops == 0:
            stops = "dir."
        elif row.max_stops > 0:
            stops = f"max {row.max_stops}sc"
        else:
            stops = "any"
        state = "✅" if row.is_active else "⏸"
        trip = f" [viaggio {row.trip_id}]" if row.trip_id else ""
        lines.append(f"{state} {row.id}. {row.name} - {row.origin}→{row.destination} {stops}{trip}")
    await update.message.reply_text("\n".join(lines))


async def trips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        trip_rows = FlightTripRepository(session).list_for_user(user.id)
        if not trip_rows:
            await update.message.reply_text("Nessun viaggio. Usa /newtrip per crearne uno.")
            return
        lines = []
        for t in trip_rows:
            legs = TravelSearchRepository(session).list_for_trip(t.id)
            lines.append(f"🗺 {t.id}. {t.name} ({len(legs)} tratt{'a' if len(legs)==1 else 'e'})")
            for leg in legs:
                lines.append(f"  · {leg.origin}→{leg.destination} {leg.date_from}")
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
        await update.message.reply_text("Indica l'id della tratta.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        ok = TravelSearchRepository(session).set_active(search_id, user.id, active)
        session.commit()
    await update.message.reply_text("Fatto." if ok else "Tratta non trovata.")


async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_enabled(update, context, True)


async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_enabled(update, context, False)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della tratta.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        ok = TravelSearchRepository(session).delete(search_id, user.id)
        session.commit()
    await update.message.reply_text("Eliminata." if ok else "Tratta non trovata.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della tratta.")
        return
    settings = get_settings()
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        row = TravelSearchRepository(session).get_for_user(search_id, user.id)
        if not row:
            await update.message.reply_text("Tratta non trovata.")
            return
        service = SearchService(session, MockFlightProvider(), DealEvaluator(settings))
        candidate = await service.check_search(row, notify=False)
    if not candidate:
        await update.message.reply_text("Nessun volo compatibile trovato ora.")
        return
    n = candidate.flight.stops
    stops_label = "diretto" if n == 0 else f"{n} scal{'o' if n == 1 else 'i'}"
    await update.message.reply_text(
        f"Controllo fatto: {candidate.total_estimated_price:.0f} EUR · "
        f"score {candidate.score:.0f}/100 · {stops_label}."
    )


async def best(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_id = _first_arg_int(context)
    if search_id is None:
        await update.message.reply_text("Indica l'id della tratta.")
        return
    with SessionLocal() as session:
        user = UserRepository(session).get_or_create(_chat_id(update), _username(update))
        row = TravelSearchRepository(session).get_for_user(search_id, user.id)
        if not row:
            await update.message.reply_text("Tratta non trovata.")
            return
        deal = DealRepository(session).get_best_for_search(search_id)
        if not deal:
            await update.message.reply_text("Non ho ancora offerte salvate per questa tratta.")
            return
        flight = deal.flight_offer
        n = flight.stops
        stops_label = "diretto" if n == 0 else f"{n} scal{'o' if n == 1 else 'i'}"
        await update.message.reply_text(
            f"Miglior volo per {row.name}:\n"
            f"{flight.origin} → {flight.destination} · {stops_label}\n"
            f"Partenza: {flight.departure_datetime:%d/%m/%Y %H:%M}\n"
            f"Prezzo: {deal.total_estimated_price:.0f} EUR · score {float(deal.score):.0f}/100\n"
            f"Prenota: {flight.booking_url}"
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
    search_conversation = ConversationHandler(
        entry_points=[CommandHandler("newsearch", newsearch)],
        states={
            SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_search_name)],
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_origin)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_destination)],
            DATE_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_date_from)],
            DATE_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_date_to)],
            FLEXIBLE_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_flexible_days)],
            ADULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_adults)],
            MAX_STOPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_max_stops)],
            MAX_FLIGHT_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_max_flight_price)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    trip_conversation = ConversationHandler(
        entry_points=[CommandHandler("newtrip", newtrip)],
        states={
            TRIP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_trip_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return [
        CommandHandler("start", start),
        CommandHandler("chatid", chatid),
        CommandHandler("help", help_command),
        search_conversation,
        trip_conversation,
        CommandHandler("searches", searches),
        CommandHandler("trips", trips),
        CommandHandler("enable", enable),
        CommandHandler("disable", disable),
        CommandHandler("delete", delete),
        CommandHandler("check", check),
        CommandHandler("best", best),
        CommandHandler("settings", settings_command),
    ]
