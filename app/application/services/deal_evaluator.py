from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.config import Settings
from app.domain.models import FlightOffer, TravelSearch
from app.domain.scoring import score_deal


@dataclass(frozen=True)
class DealCandidate:
    search: TravelSearch
    flight: FlightOffer
    total_estimated_price: Decimal
    score: float
    previous_best_price: Decimal | None
    previous_best_score: float | None

    @property
    def price_improvement_percent(self) -> float:
        if not self.previous_best_price or self.previous_best_price <= 0:
            return 0
        ratio = (self.previous_best_price - self.total_estimated_price) / self.previous_best_price
        return round(float(ratio) * 100, 2)

    @property
    def score_improvement(self) -> float:
        if self.previous_best_score is None:
            return 0
        return round(self.score - self.previous_best_score, 2)


class DealEvaluator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_candidate(
        self,
        search: TravelSearch,
        flight: FlightOffer,
        previous_best_price: Decimal | None,
        previous_best_score: float | None,
    ) -> DealCandidate:
        return DealCandidate(
            search=search,
            flight=flight,
            total_estimated_price=flight.total_price,
            score=score_deal(search, flight, previous_best_price),
            previous_best_price=previous_best_price,
            previous_best_score=previous_best_score,
        )

    def should_notify(self, candidate: DealCandidate) -> bool:
        under_budget = candidate.total_estimated_price <= candidate.search.max_budget_total
        price_improved = (
            candidate.price_improvement_percent >= self.settings.min_price_improvement_percent
        )
        score_improved = candidate.score_improvement >= self.settings.min_score_improvement
        first_good = candidate.previous_best_price is None and under_budget
        return first_good or under_budget or price_improved or score_improved
