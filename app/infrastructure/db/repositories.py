from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.domain.models import FlightOffer, FlightTrip, TravelSearch, User
from app.infrastructure.db.models import (
    DealSnapshotORM,
    FlightOfferORM,
    FlightTripORM,
    NotificationLogORM,
    TravelSearchORM,
    UserORM,
)


def user_to_domain(row: UserORM) -> User:
    return User(row.id, row.telegram_chat_id, row.username, row.created_at)


def trip_to_domain(row: FlightTripORM) -> FlightTrip:
    return FlightTrip(row.id, row.user_id, row.name, row.created_at)


def search_to_domain(row: TravelSearchORM) -> TravelSearch:
    return TravelSearch(
        id=row.id,
        user_id=row.user_id,
        name=row.name,
        origin=row.origin,
        destination=row.destination,
        date_from=row.date_from,
        date_to=row.date_to,
        flexible_days=row.flexible_days,
        adults=row.adults,
        children=row.children,
        max_budget_total=row.max_budget_total,
        max_flight_price=row.max_flight_price,
        max_stops=row.max_stops,
        preferred_departure_time_window=row.preferred_departure_time_window,
        preferred_return_time_window=row.preferred_return_time_window,
        is_active=row.is_active,
        check_frequency_minutes=row.check_frequency_minutes,
        trip_id=row.trip_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(self, telegram_chat_id: int, username: str | None) -> UserORM:
        user = self.session.scalar(
            select(UserORM).where(UserORM.telegram_chat_id == telegram_chat_id)
        )
        if user:
            if username and user.username != username:
                user.username = username
            return user
        user = UserORM(telegram_chat_id=telegram_chat_id, username=username)
        self.session.add(user)
        self.session.flush()
        return user


class FlightTripRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user_id: int, name: str) -> FlightTripORM:
        row = FlightTripORM(user_id=user_id, name=name)
        self.session.add(row)
        self.session.flush()
        return row

    def get(self, trip_id: int) -> FlightTripORM | None:
        return self.session.get(FlightTripORM, trip_id)

    def get_for_user(self, trip_id: int, user_id: int) -> FlightTripORM | None:
        return self.session.scalar(
            select(FlightTripORM).where(
                FlightTripORM.id == trip_id, FlightTripORM.user_id == user_id
            )
        )

    def list_for_user(self, user_id: int) -> list[FlightTripORM]:
        return list(
            self.session.scalars(
                select(FlightTripORM)
                .where(FlightTripORM.user_id == user_id)
                .order_by(FlightTripORM.id)
            )
        )

    def delete(self, trip_id: int, user_id: int) -> bool:
        row = self.get_for_user(trip_id, user_id)
        if not row:
            return False
        self.session.delete(row)
        return True


class TravelSearchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, search: TravelSearch) -> TravelSearchORM:
        excluded = {"id", "created_at", "updated_at"}
        row = TravelSearchORM(**{k: v for k, v in asdict(search).items() if k not in excluded})
        self.session.add(row)
        self.session.flush()
        return row

    def list_all(self) -> list[TravelSearchORM]:
        return list(self.session.scalars(select(TravelSearchORM).order_by(TravelSearchORM.id)))

    def list_for_user(self, user_id: int) -> list[TravelSearchORM]:
        return list(
            self.session.scalars(
                select(TravelSearchORM)
                .where(TravelSearchORM.user_id == user_id)
                .order_by(TravelSearchORM.id)
            )
        )

    def list_for_trip(self, trip_id: int) -> list[TravelSearchORM]:
        return list(
            self.session.scalars(
                select(TravelSearchORM)
                .where(TravelSearchORM.trip_id == trip_id)
                .order_by(TravelSearchORM.id)
            )
        )

    def list_active(self) -> list[TravelSearchORM]:
        return list(
            self.session.scalars(select(TravelSearchORM).where(TravelSearchORM.is_active.is_(True)))
        )

    def get(self, search_id: int) -> TravelSearchORM | None:
        return self.session.get(TravelSearchORM, search_id)

    def get_for_user(self, search_id: int, user_id: int) -> TravelSearchORM | None:
        return self.session.scalar(
            select(TravelSearchORM).where(
                TravelSearchORM.id == search_id, TravelSearchORM.user_id == user_id
            )
        )

    def set_active(self, search_id: int, user_id: int, active: bool) -> bool:
        row = self.get_for_user(search_id, user_id)
        if not row:
            return False
        row.is_active = active
        return True

    def delete(self, search_id: int, user_id: int) -> bool:
        row = self.get_for_user(search_id, user_id)
        if not row:
            return False
        self.session.delete(row)
        return True


class DealRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_flight(self, offer: FlightOffer) -> FlightOfferORM:
        row = FlightOfferORM(**{k: v for k, v in asdict(offer).items() if k != "id"})
        self.session.add(row)
        self.session.flush()
        return row

    def save_snapshot(
        self,
        search_id: int,
        flight_offer_id: int | None,
        total_estimated_price: Decimal,
        score: float,
        is_notified: bool = False,
    ) -> DealSnapshotORM:
        row = DealSnapshotORM(
            search_id=search_id,
            flight_offer_id=flight_offer_id,
            total_estimated_price=total_estimated_price,
            score=score,
            is_notified=is_notified,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def get_best_for_search(self, search_id: int) -> DealSnapshotORM | None:
        stmt: Select[tuple[DealSnapshotORM]] = (
            select(DealSnapshotORM)
            .options(joinedload(DealSnapshotORM.flight_offer))
            .where(DealSnapshotORM.search_id == search_id)
            .order_by(DealSnapshotORM.score.desc(), DealSnapshotORM.total_estimated_price.asc())
            .limit(1)
        )
        return self.session.scalar(stmt)

    def get_best_price_for_search(self, search_id: int) -> Decimal | None:
        return self.session.scalar(
            select(func.min(DealSnapshotORM.total_estimated_price)).where(
                DealSnapshotORM.search_id == search_id
            )
        )

    def list_for_search(self, search_id: int, limit: int = 20) -> list[DealSnapshotORM]:
        return list(
            self.session.scalars(
                select(DealSnapshotORM)
                .options(joinedload(DealSnapshotORM.flight_offer))
                .where(DealSnapshotORM.search_id == search_id)
                .order_by(DealSnapshotORM.created_at.desc())
                .limit(limit)
            )
        )

    def mark_notified(self, snapshot_id: int) -> None:
        snapshot = self.session.get(DealSnapshotORM, snapshot_id)
        if snapshot:
            snapshot.is_notified = True


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user_id: int, search_id: int, message: str, notification_type: str) -> None:
        self.session.add(
            NotificationLogORM(
                user_id=user_id,
                search_id=search_id,
                message=message,
                notification_type=notification_type,
            )
        )

    def has_recent_identical(
        self, user_id: int, search_id: int, message: str, cooldown_hours: int
    ) -> bool:
        since = datetime.utcnow() - timedelta(hours=cooldown_hours)
        stmt = select(NotificationLogORM).where(
            NotificationLogORM.user_id == user_id,
            NotificationLogORM.search_id == search_id,
            NotificationLogORM.message == message,
            NotificationLogORM.sent_at >= since,
        )
        return self.session.scalar(stmt) is not None
