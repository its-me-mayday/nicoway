from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.models import TravelSearch
from app.infrastructure.db.models import Base
from app.infrastructure.db.repositories import TravelSearchRepository, UserRepository


@pytest.fixture()
def session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    local_session = sessionmaker(bind=engine, expire_on_commit=False)
    with local_session() as db:
        yield db


@pytest.fixture()
def sample_search() -> TravelSearch:
    return TravelSearch(
        id=1,
        user_id=1,
        name="Scozia 2026",
        origin="FCO",
        destination="EDI",
        date_from=date(2026, 8, 31),
        date_to=date(2026, 9, 7),
        flexible_days=2,
        adults=2,
        children=0,
        max_budget_total=Decimal("350"),
        max_flight_price=Decimal("350"),
        max_stops=0,
        preferred_departure_time_window="07-11",
        preferred_return_time_window="16-21",
        is_active=True,
        check_frequency_minutes=180,
    )


@pytest.fixture()
def persisted_search(session: Session, sample_search: TravelSearch):
    user = UserRepository(session).get_or_create(12345, "luca")
    sample_search.id = None
    sample_search.user_id = user.id
    row = TravelSearchRepository(session).add(sample_search)
    session.commit()
    return row
