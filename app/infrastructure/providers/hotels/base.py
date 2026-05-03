from abc import ABC, abstractmethod

from app.domain.models import HotelOffer, TravelSearch


class HotelProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, search: TravelSearch) -> list[HotelOffer]:
        """Return normalized hotel offers for a travel search."""
