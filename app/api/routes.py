from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.services.deal_evaluator import DealEvaluator
from app.application.services.search_service import SearchService
from app.config import Settings, get_settings
from app.infrastructure.db.repositories import DealRepository, TravelSearchRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.providers.flights.mock_provider import MockFlightProvider
from app.infrastructure.providers.hotels.mock_provider import MockHotelProvider

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


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


@router.get("/health")
def health(settings: SettingsDep) -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@router.get("/searches")
def list_searches(session: SessionDep) -> list[dict]:
    return [serialize_search(row) for row in TravelSearchRepository(session).list_all()]


@router.get("/searches/{search_id}")
def get_search(search_id: int, session: SessionDep) -> dict:
    row = TravelSearchRepository(session).get(search_id)
    if not row:
        raise HTTPException(status_code=404, detail="Search not found")
    return serialize_search(row)


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
    return [
        {
            "id": deal.id,
            "total_estimated_price": deal.total_estimated_price,
            "score": float(deal.score),
            "is_notified": deal.is_notified,
            "created_at": deal.created_at,
        }
        for deal in deals
    ]
