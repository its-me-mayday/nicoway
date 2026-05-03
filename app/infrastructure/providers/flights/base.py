from abc import ABC, abstractmethod

from app.domain.models import FlightOffer, TravelSearch


class FlightProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, search: TravelSearch) -> list[FlightOffer]:
        """Return normalized flight offers for a travel search."""
