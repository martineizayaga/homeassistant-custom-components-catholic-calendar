"""Tests for the Catholic Calendar coordinator."""

from __future__ import annotations

import datetime
from typing import Any

from custom_components.catholic_calendar.coordinator import CatholicCalendarCoordinator

def test_festivity_precedence_sorting(coordinator: CatholicCalendarCoordinator) -> None:
    """Test that festivities are correctly sorted by grade (importance)."""
    
    # Manually inject unsorted festivities for a specific date
    target_date = datetime.datetime(2026, 3, 7)
    unsorted_events = [
        {"name": "Lower Rank Event", "liturgical_grade": 0},
        {"name": "Higher Rank Event", "liturgical_grade": 6},
        {"name": "Middle Rank Event", "liturgical_grade": 3},
    ]
    
    coordinator.festivities[target_date] = unsorted_events
    
    # Run the internal update logic (which now includes the sort)
    coordinator._update_data()
    
    sorted_events = coordinator.festivities[target_date]
    
    # Assertions
    assert sorted_events[0]["name"] == "Higher Rank Event"
    assert sorted_events[1]["name"] == "Middle Rank Event"
    assert sorted_events[2]["name"] == "Lower Rank Event"

def test_vespers_early_switch(coordinator: CatholicCalendarCoordinator) -> None:
    """Test that Sundays/Solemnities trigger an early switch at 4:00 PM."""
    
    sunday = datetime.datetime(2026, 3, 8)
    coordinator.festivities[sunday] = [
        {"name": "Sunday Feast", "liturgical_grade": 7}
    ]
    
    # Scenario A: Saturday 3:59 PM (Should NOT switch)
    sat_359 = datetime.datetime(2026, 3, 7, 15, 59, 0)
    assert coordinator.get_liturgical_date(sat_359) == sat_359.date()
    
    # Scenario B: Saturday 4:00 PM (Should switch to Sunday)
    sat_400 = datetime.datetime(2026, 3, 7, 16, 0, 0)
    assert coordinator.get_liturgical_date(sat_400) == sunday.date()
