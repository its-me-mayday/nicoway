from datetime import date

from app.application.services.itinerary_assistant import ItineraryAssistant


def test_itinerary_assistant_builds_searchable_plan_from_natural_prompt():
    plan = ItineraryAssistant().build_plan(
        "Parto da Roma con mia moglie per Edimburgo a fine agosto 2026, "
        "budget 1800 euro, hotel romantico centrale.",
        today=date(2026, 5, 3),
    )

    assert plan.draft.origin == "FCO"
    assert plan.draft.destination == "Edimburgo"
    assert plan.draft.date_from == date(2026, 8, 24)
    assert plan.draft.adults == 2
    assert plan.draft.max_budget_total == 1800
    assert plan.draft.min_hotel_stars == 4
    assert plan.advice.hotel_strategy
    assert "Prenota" in plan.advice.booking_advice
