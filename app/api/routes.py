from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.services.deal_evaluator import DealEvaluator
from app.application.services.search_service import SearchService
from app.config import Settings, get_settings
from app.domain.models import TravelSearch
from app.infrastructure.db.repositories import (
    DealRepository,
    FlightTripRepository,
    TravelSearchRepository,
    UserRepository,
)
import httpx

from app.infrastructure.db.session import get_session
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.flights.travelpayouts_provider import TravelpayoutsFlightProvider
from app import log_buffer

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


class FlightSearchCreate(BaseModel):
    telegram_chat_id: int
    username: str | None = None
    name: str
    origin: str
    destination: str
    date_from: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    date_to: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    flexible_days: int = 0
    adults: int = 2
    children: int = 0
    max_budget_total: float
    max_flight_price: float | None = None
    max_stops: int = 0  # 0=diretto, -1=qualsiasi, N=max N scali
    preferred_departure_time_window: str | None = "07-11"
    preferred_return_time_window: str | None = "16-21"
    check_frequency_minutes: int | None = None
    trip_id: int | None = None


class TripLegCreate(BaseModel):
    name: str
    origin: str
    destination: str
    departure_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    adults: int = 2
    children: int = 0
    max_budget_total: float
    max_flight_price: float | None = None
    max_stops: int = 0
    preferred_departure_time_window: str | None = "07-11"


class TripCreate(BaseModel):
    telegram_chat_id: int
    username: str | None = None
    name: str
    legs: list[TripLegCreate] = Field(min_length=1)
    check_frequency_minutes: int | None = None


def _persist_search(
    payload: FlightSearchCreate,
    session: Session,
    settings: Settings,
) -> object:
    user = UserRepository(session).get_or_create(payload.telegram_chat_id, payload.username)
    return TravelSearchRepository(session).add(
        TravelSearch(
            id=None,
            user_id=user.id,
            name=payload.name,
            origin=payload.origin.upper(),
            destination=payload.destination.upper(),
            date_from=date.fromisoformat(payload.date_from),
            date_to=date.fromisoformat(payload.date_to),
            flexible_days=payload.flexible_days,
            adults=payload.adults,
            children=payload.children,
            max_budget_total=Decimal(str(payload.max_budget_total)),
            max_flight_price=(
                Decimal(str(payload.max_flight_price)) if payload.max_flight_price else None
            ),
            max_stops=payload.max_stops,
            preferred_departure_time_window=payload.preferred_departure_time_window,
            preferred_return_time_window=payload.preferred_return_time_window,
            is_active=True,
            check_frequency_minutes=(
                payload.check_frequency_minutes or settings.default_check_frequency_minutes
            ),
            trip_id=payload.trip_id,
        )
    )


def _serialize_search(row) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "trip_id": row.trip_id,
        "name": row.name,
        "origin": row.origin,
        "destination": row.destination,
        "date_from": row.date_from,
        "date_to": row.date_to,
        "flexible_days": row.flexible_days,
        "adults": row.adults,
        "children": row.children,
        "max_budget_total": row.max_budget_total,
        "max_flight_price": row.max_flight_price,
        "max_stops": row.max_stops,
        "preferred_departure_time_window": row.preferred_departure_time_window,
        "preferred_return_time_window": row.preferred_return_time_window,
        "is_active": row.is_active,
        "check_frequency_minutes": row.check_frequency_minutes,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _serialize_trip(trip_row, legs: list) -> dict:
    return {
        "id": trip_row.id,
        "name": trip_row.name,
        "created_at": trip_row.created_at,
        "legs": [_serialize_search(leg) for leg in legs],
    }


def _serialize_deal(deal) -> dict:
    flight = deal.flight_offer
    return {
        "id": deal.id,
        "total_estimated_price": deal.total_estimated_price,
        "score": float(deal.score),
        "is_notified": deal.is_notified,
        "created_at": deal.created_at,
        "flight": {
            "provider": flight.provider,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_datetime": flight.departure_datetime,
            "arrival_datetime": flight.arrival_datetime,
            "return_departure_datetime": flight.return_departure_datetime,
            "total_price": flight.total_price,
            "currency": flight.currency,
            "stops": flight.stops,
            "duration_minutes": flight.duration_minutes,
            "booking_url": flight.booking_url,
            "airline": flight.airline,
        } if flight else None,
    }


@router.get("/health")
def health(settings: SettingsDep) -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@router.get("/logs")
def get_logs(since: int = 0) -> list[dict]:
    return log_buffer.get_entries(since_ms=since)


@router.get("/fares/calendar")
async def fare_calendar(
    origin: str,
    destination: str,
    month: str,  # YYYY-MM
    settings: SettingsDep,
) -> dict:
    token = settings.travelpayouts_token
    if not token:
        raise HTTPException(status_code=503, detail="Travelpayouts token non configurato")
    params = {
        "origin": origin.upper()[:3],
        "destination": destination.upper()[:3],
        "depart_date": f"{month}-01",
        "currency": "eur",
        "token": token,
        "calendar_type": "departure_date",
        "one_way": "true",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get("https://api.travelpayouts.com/v1/prices/calendar", params=params)
        r.raise_for_status()
        payload = r.json()
    if not payload.get("success"):
        return {"days": []}
    days = []
    for day_str, info in sorted(payload.get("data", {}).items()):
        days.append({
            "date": day_str,
            "price": info.get("price"),
            "airline": info.get("airline"),
            "stops": info.get("number_of_changes", 0),
            "departure_at": info.get("departure_at"),
            "duration_to": info.get("duration_to"),
        })
    return {"origin": origin.upper()[:3], "destination": destination.upper()[:3], "month": month, "days": days}


# --- Searches ---

@router.get("/searches")
def list_searches(session: SessionDep, telegram_chat_id: int | None = None) -> list[dict]:
    repo = TravelSearchRepository(session)
    if telegram_chat_id is not None:
        user = UserRepository(session).get_or_create(telegram_chat_id, None)
        rows = repo.list_for_user(user.id)
    else:
        rows = repo.list_all()
    return [_serialize_search(row) for row in rows]


@router.post("/searches")
def create_search(payload: FlightSearchCreate, session: SessionDep, settings: SettingsDep) -> dict:
    row = _persist_search(payload, session, settings)
    session.commit()
    return _serialize_search(row)


@router.get("/searches/{search_id}")
def get_search(search_id: int, session: SessionDep) -> dict:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    return _serialize_search(row)


@router.post("/searches/{search_id}/enable")
def enable_search(search_id: int, session: SessionDep) -> dict[str, bool]:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    row.is_active = True
    session.commit()
    return {"ok": True}


@router.post("/searches/{search_id}/disable")
def disable_search(search_id: int, session: SessionDep) -> dict[str, bool]:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    row.is_active = False
    session.commit()
    return {"ok": True}


@router.delete("/searches/{search_id}")
def delete_search(search_id: int, session: SessionDep) -> dict[str, bool]:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    session.delete(row)
    session.commit()
    return {"ok": True}


@router.post("/searches/{search_id}/check")
async def check_search(search_id: int, session: SessionDep, settings: SettingsDep) -> dict:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    provider = (
        TravelpayoutsFlightProvider(settings.travelpayouts_token)
        if settings.travelpayouts_token
        else MockFlightProvider()
    )
    service = SearchService(session, provider, DealEvaluator(settings))
    candidate = await service.check_search(row, notify=False)
    if not candidate:
        return {"status": "no_deals"}
    return {
        "status": "checked",
        "total_estimated_price": candidate.total_estimated_price,
        "score": candidate.score,
    }


@router.get("/deals/{search_id}")
def list_deals(search_id: int, session: SessionDep) -> list[dict]:
    return [_serialize_deal(deal) for deal in DealRepository(session).list_for_search(search_id)]


# --- Trips ---

@router.post("/trips")
def create_trip(payload: TripCreate, session: SessionDep, settings: SettingsDep) -> dict:
    user = UserRepository(session).get_or_create(payload.telegram_chat_id, payload.username)
    trip = FlightTripRepository(session).add(user.id, payload.name)
    legs = []
    for leg in payload.legs:
        row = TravelSearchRepository(session).add(
            TravelSearch(
                id=None,
                user_id=user.id,
                name=leg.name,
                origin=leg.origin.upper(),
                destination=leg.destination.upper(),
                date_from=date.fromisoformat(leg.departure_date),
                date_to=date.fromisoformat(leg.departure_date),
                flexible_days=0,
                adults=leg.adults,
                children=leg.children,
                max_budget_total=Decimal(str(leg.max_budget_total)),
                max_flight_price=(
                    Decimal(str(leg.max_flight_price)) if leg.max_flight_price else None
                ),
                max_stops=leg.max_stops,
                preferred_departure_time_window=leg.preferred_departure_time_window,
                preferred_return_time_window=None,
                is_active=True,
                check_frequency_minutes=(
                    payload.check_frequency_minutes or settings.default_check_frequency_minutes
                ),
                trip_id=trip.id,
            )
        )
        legs.append(row)
    session.commit()
    return _serialize_trip(trip, legs)


@router.get("/trips")
def list_trips(telegram_chat_id: int, session: SessionDep) -> list[dict]:
    user = UserRepository(session).get_or_create(telegram_chat_id, None)
    trips = FlightTripRepository(session).list_for_user(user.id)
    result = []
    for trip in trips:
        legs = TravelSearchRepository(session).list_for_trip(trip.id)
        result.append(_serialize_trip(trip, legs))
    return result


@router.get("/trips/{trip_id}")
def get_trip(trip_id: int, session: SessionDep) -> dict:
    trip = FlightTripRepository(session).get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    legs = TravelSearchRepository(session).list_for_trip(trip_id)
    return _serialize_trip(trip, legs)


@router.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, session: SessionDep) -> dict[str, bool]:
    trip = FlightTripRepository(session).get(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    session.delete(trip)
    session.commit()
    return {"ok": True}
