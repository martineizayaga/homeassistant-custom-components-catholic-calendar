"""DataUpdateCoordinator for the Catholic Calendar integration."""

from __future__ import annotations

import datetime
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calendar_generator import CalendarGenerator
from .liturgical_grade import LiturgicalGrade

_LOGGER = logging.getLogger(__name__)


class CatholicCalendarCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Catholic Calendar data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="catholic_calendar",
            update_interval=datetime.timedelta(hours=12),
        )
        self.years_loaded: set[int] = set()
        self.festivities: dict[datetime.datetime, list[dict[str, Any]]] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via executor."""
        return await self.hass.async_add_executor_job(self._update_data)

    def _update_data(self) -> dict[str, Any]:
        """Fetch data from calendar generator."""
        today = dt_util.now().date()
        
        # We always want the current year and the next year (for upcoming events)
        years_to_load = [today.year, today.year + 1]
        
        for year in years_to_load:
            if year not in self.years_loaded:
                _LOGGER.debug("Generating festivities for year %s", year)
                gen = CalendarGenerator(year)
                year_festivities = gen.generate_festivities()
                
                for date_key, events in year_festivities.items():
                    # Process and enrich events only if not already in festivities
                    if date_key not in self.festivities:
                        self.festivities[date_key] = []
                        for event in events:
                            enriched_event = dict(event)
                            grade = enriched_event.get("liturgical_grade", 0)
                            enriched_event["liturgical_grade_desc"] = (
                                LiturgicalGrade.descr(int(grade)) or "Unknown"
                            )
                            self.festivities[date_key].append(enriched_event)
                
                self.years_loaded.add(year)

        # Prune old festivities (older than 1 year) to save memory
        cutoff = datetime.datetime(today.year - 1, today.month, today.day)
        self.festivities = {
            k: v for k, v in self.festivities.items() if k >= cutoff
        }
        self.years_loaded = {y for y in self.years_loaded if y >= today.year - 1}

        # Get current season
        current_gen = CalendarGenerator(today.year)
        season = current_gen.get_season(today)

        # Get today's festivities
        todays_festivities = []
        date_key = datetime.datetime(today.year, today.month, today.day)
        if date_key in self.festivities:
            todays_festivities = sorted(
                self.festivities[date_key], 
                key=lambda x: x.get("liturgical_grade", 0), 
                reverse=True
            )

        return {
            "today": today,
            "season": season.value,
            "festivities": todays_festivities,
            "all_festivities": self.festivities,  # Needed for the calendar
        }
