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
    TravelSearchRepository,
    UserRepository,
)
from app.infrastructure.db.session import get_session
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


class TravelSearchCreate(BaseModel):
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
    max_hotel_price_per_night: float | None = None
    min_hotel_stars: int | None = 3
    preferred_departure_time_window: str | None = "07-11"
    preferred_return_time_window: str | None = "16-21"
    check_frequency_minutes: int | None = None


def serialize_search(row) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
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
        "max_hotel_price_per_night": row.max_hotel_price_per_night,
        "min_hotel_stars": row.min_hotel_stars,
        "preferred_departure_time_window": row.preferred_departure_time_window,
        "preferred_return_time_window": row.preferred_return_time_window,
        "is_active": row.is_active,
        "check_frequency_minutes": row.check_frequency_minutes,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def serialize_deal(deal) -> dict:
    flight = deal.flight_offer
    hotel = deal.hotel_offer
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
            "return_departure_datetime": flight.return_departure_datetime,
            "total_price": flight.total_price,
            "currency": flight.currency,
            "stops": flight.stops,
            "duration_minutes": flight.duration_minutes,
            "booking_url": flight.booking_url,
        }
        if flight
        else None,
        "hotel": {
            "provider": hotel.provider,
            "hotel_name": hotel.hotel_name,
            "destination": hotel.destination,
            "checkin_date": hotel.checkin_date,
            "checkout_date": hotel.checkout_date,
            "price_per_night": hotel.price_per_night,
            "total_price": hotel.total_price,
            "currency": hotel.currency,
            "stars": hotel.stars,
            "rating": float(hotel.rating),
            "booking_url": hotel.booking_url,
        }
        if hotel
        else None,
    }


@router.get("/health")
def health(settings: SettingsDep) -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@router.get("/searches")
def list_searches(session: SessionDep) -> list[dict]:
    return [serialize_search(row) for row in TravelSearchRepository(session).list_all()]


@router.post("/searches")
def create_search(
    payload: TravelSearchCreate,
    session: SessionDep,
    settings: SettingsDep,
) -> dict:
    from datetime import date
    from decimal import Decimal

    user = UserRepository(session).get_or_create(payload.telegram_chat_id, payload.username)
    row = TravelSearchRepository(session).add(
        TravelSearch(
            id=None,
            user_id=user.id,
            name=payload.name,
            origin=payload.origin.upper(),
            destination=payload.destination,
            date_from=date.fromisoformat(payload.date_from),
            date_to=date.fromisoformat(payload.date_to),
            flexible_days=payload.flexible_days,
            adults=payload.adults,
            children=payload.children,
            max_budget_total=Decimal(str(payload.max_budget_total)),
            max_flight_price=Decimal(str(payload.max_flight_price))
            if payload.max_flight_price is not None
            else None,
            max_hotel_price_per_night=Decimal(str(payload.max_hotel_price_per_night))
            if payload.max_hotel_price_per_night is not None
            else None,
            min_hotel_stars=payload.min_hotel_stars,
            preferred_departure_time_window=payload.preferred_departure_time_window,
            preferred_return_time_window=payload.preferred_return_time_window,
            is_active=True,
            check_frequency_minutes=(
                payload.check_frequency_minutes or settings.default_check_frequency_minutes
            ),
        )
    )
    session.commit()
    return serialize_search(row)


@router.get("/searches/{search_id}")
def get_search(search_id: int, session: SessionDep) -> dict:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    return serialize_search(row)


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
async def check_search(
    search_id: int,
    session: SessionDep,
    settings: SettingsDep,
) -> dict:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    service = SearchService(
        session,
        MockFlightProvider(),
        MockHotelProvider(),
        DealEvaluator(settings),
        notification_service=None,
    )
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
    deals = DealRepository(session).list_for_search(search_id)
    return [serialize_deal(deal) for deal in deals]
