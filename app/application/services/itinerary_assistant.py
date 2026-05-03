from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

MONTHS = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}

AIRPORT_HINTS = {
    "roma": "FCO",
    "fiumicino": "FCO",
    "ciampino": "CIA",
    "milano": "MXP",
    "malpensa": "MXP",
    "linate": "LIN",
    "bergamo": "BGY",
    "napoli": "NAP",
    "venezia": "VCE",
    "bologna": "BLQ",
    "torino": "TRN",
    "pisa": "PSA",
}

DESTINATION_ALIASES = {
    "edinburgh": "Edimburgo",
    "edimburgo": "Edimburgo",
    "scozia": "Edimburgo",
    "parigi": "Parigi",
    "londra": "Londra",
    "lisbona": "Lisbona",
    "porto": "Porto",
    "barcellona": "Barcellona",
    "praga": "Praga",
    "vienna": "Vienna",
    "amsterdam": "Amsterdam",
    "islanda": "Reykjavik",
    "reykjavik": "Reykjavik",
}


@dataclass(frozen=True)
class ItineraryDraft:
    name: str
    origin: str
    destination: str
    date_from: date
    date_to: date
    flexible_days: int
    adults: int
    children: int
    max_budget_total: float
    max_flight_price: float | None
    max_hotel_price_per_night: float | None
    min_hotel_stars: int
    preferred_departure_time_window: str
    preferred_return_time_window: str


@dataclass(frozen=True)
class ItineraryAdvice:
    hotel_strategy: list[str]
    experiences: list[str]
    timing: list[str]
    booking_advice: str
    assumptions: list[str]


@dataclass(frozen=True)
class ItineraryPlan:
    draft: ItineraryDraft
    advice: ItineraryAdvice


class ItineraryAssistant:
    def build_plan(self, prompt: str, today: date | None = None) -> ItineraryPlan:
        today = today or date.today()
        normalized = prompt.lower()
        destination = self._extract_destination(normalized)
        origin = self._extract_origin(normalized)
        date_from, date_to = self._extract_dates(normalized, today)
        adults = self._extract_adults(normalized)
        budget = self._extract_budget(normalized)
        hotel_cap = self._extract_hotel_cap(normalized, budget, date_from, date_to)
        flight_cap = self._extract_flight_cap(normalized, budget)
        flexible_days = (
            3
            if any(word in normalized for word in ["flessibile", "flex", "circa"])
            else 1
        )
        min_stars = 4 if any(word in normalized for word in ["romantico", "bello", "charme"]) else 3

        draft = ItineraryDraft(
            name=f"{destination} {date_from.year}",
            origin=origin,
            destination=destination,
            date_from=date_from,
            date_to=date_to,
            flexible_days=flexible_days,
            adults=adults,
            children=0,
            max_budget_total=budget,
            max_flight_price=flight_cap,
            max_hotel_price_per_night=hotel_cap,
            min_hotel_stars=min_stars,
            preferred_departure_time_window="07-11",
            preferred_return_time_window="16-21",
        )
        return ItineraryPlan(draft=draft, advice=self._build_advice(draft, normalized))

    def _extract_origin(self, text: str) -> str:
        for hint, code in AIRPORT_HINTS.items():
            if re.search(rf"\b(da|parto da|partenza da)\s+{hint}\b", text) or hint in text:
                return code
        match = re.search(r"\b([a-z]{3})\b", text)
        return match.group(1).upper() if match else "FCO"

    def _extract_destination(self, text: str) -> str:
        for hint, destination in DESTINATION_ALIASES.items():
            if hint in text:
                return destination
        match = re.search(r"\b(?:a|per|verso|destinazione)\s+([a-zà-ù\s]{3,28})", text)
        if match:
            raw = re.split(r"\s+(?:da|dal|con|per|budget|fine|inizio|metà)", match.group(1))[0]
            return raw.strip().title() or "Edimburgo"
        return "Edimburgo"

    def _extract_dates(self, text: str, today: date) -> tuple[date, date]:
        explicit = re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text)
        if len(explicit) >= 2:
            first = date(*(int(part) for part in explicit[0]))
            second = date(*(int(part) for part in explicit[1]))
            return first, second
        if len(explicit) == 1:
            first = date(*(int(part) for part in explicit[0]))
            return first, first + timedelta(days=7)

        year_match = re.search(r"\b(20\d{2})\b", text)
        month = next((number for label, number in MONTHS.items() if label in text), None)
        year = int(year_match.group(1)) if year_match else today.year
        if month is None:
            month = today.month + 2
            if month > 12:
                month -= 12
                year += 1
        if date(year, month, 1) < today.replace(day=1):
            year += 1

        day = 15
        if "inizio" in text:
            day = 5
        elif "fine" in text:
            day = 24
        elif "metà" in text or "meta" in text:
            day = 15

        nights = self._extract_nights(text)
        start = date(year, month, min(day, 28))
        return start, start + timedelta(days=nights)

    def _extract_nights(self, text: str) -> int:
        night_match = re.search(r"(\d{1,2})\s*(?:notti|giorni|gg)", text)
        if night_match:
            return max(1, min(21, int(night_match.group(1))))
        week_match = re.search(r"(\d{1,2})\s*(?:settimane|settimana)", text)
        if week_match:
            return max(3, min(28, int(week_match.group(1)) * 7))
        return 7

    def _extract_adults(self, text: str) -> int:
        if "mia moglie" in text or "coppia" in text or "noi due" in text:
            return 2
        match = re.search(r"(\d{1,2})\s*(?:adulti|persone|pax)", text)
        return max(1, min(8, int(match.group(1)))) if match else 2

    def _extract_budget(self, text: str) -> float:
        budget_match = re.search(r"(?:budget|massimo|max|entro)\s*(?:di)?\s*(\d{3,5})", text)
        if budget_match:
            return float(budget_match.group(1))
        euro_match = re.search(r"(\d{3,5})\s*(?:€|eur|euro)", text)
        return float(euro_match.group(1)) if euro_match else 1800.0

    def _extract_hotel_cap(self, text: str, budget: float, date_from: date, date_to: date) -> float:
        hotel_match = re.search(r"(?:hotel|notte|notte max|max hotel)[^\d]*(\d{2,4})", text)
        if hotel_match:
            return float(hotel_match.group(1))
        nights = max((date_to - date_from).days, 1)
        return round(min(180.0, max(70.0, budget * 0.45 / nights)), 0)

    def _extract_flight_cap(self, text: str, budget: float) -> float:
        flight_match = re.search(r"(?:volo|voli|flight)[^\d]*(\d{2,4})", text)
        if flight_match:
            return float(flight_match.group(1))
        return round(min(600.0, max(150.0, budget * 0.28)), 0)

    def _build_advice(self, draft: ItineraryDraft, text: str) -> ItineraryAdvice:
        destination = draft.destination
        hotel_tone = "boutique o guesthouse curata" if "romantico" in text else "hotel centrale"
        hotel_strategy = [
            f"Cerca un {hotel_tone} con cancellazione gratuita nelle prime 48 ore.",
            "Preferisci una zona raggiungibile a piedi la sera: riduce taxi e tempi morti.",
            f"Soglia sensata per ora: circa {draft.max_hotel_price_per_night:.0f} EUR/notte.",
        ]
        experiences = [
            (
                f"Prima sera: passeggiata lenta nel centro di {destination} "
                "e cena senza incastri stretti."
            ),
            (
                "Seconda giornata: esperienza guidata al mattino, "
                "pomeriggio libero per quartieri e cafe."
            ),
            (
                "Ultimo giorno: tieni una finestra leggera, utile se il volo "
                "rientra nel tardo pomeriggio."
            ),
        ]
        timing = [
            "Partenza ideale tra 07:00 e 11:00: arrivate con luce e sfruttate il primo giorno.",
            "Ritorno ideale tra 16:00 e 21:00: evita una notte sprecata e resta comodo.",
            "Per hotel romantici piccoli, blocca prima una tariffa cancellabile e rivaluta dopo.",
        ]
        booking_advice = (
            "Prenota se trovi un totale sotto budget con score alto e hotel cancellabile. "
            "Aspetta se il volo ha scali lunghi o se il risparmio non supera circa il 10%."
        )
        assumptions = [
            "Ho stimato le date dal testo quando non erano puntuali.",
            "Le esperienze sono suggerimenti editoriali locali, non inventario prenotabile reale.",
            "I prezzi arrivano dai provider mock finché non colleghiamo API reali.",
        ]
        return ItineraryAdvice(
            hotel_strategy=hotel_strategy,
            experiences=experiences,
            timing=timing,
            booking_advice=booking_advice,
            assumptions=assumptions,
        )
