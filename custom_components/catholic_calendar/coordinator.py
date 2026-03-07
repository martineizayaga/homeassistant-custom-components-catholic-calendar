"""DataUpdateCoordinator for the Catholic Calendar integration."""

from __future__ import annotations

import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calendar_generator import CalendarGenerator
from .liturgical_grade import LiturgicalGrade
from .liturgical_season import LiturgicalSeason

_LOGGER = logging.getLogger(__name__)


class CatholicCalendarCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Catholic Calendar data."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry | None = None
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="catholic_calendar",
            update_interval=datetime.timedelta(hours=12),
        )
        self.years_loaded: set[int] = set()
        self.festivities: dict[datetime.datetime, list[dict[str, Any]]] = {}

    def get_liturgical_date(self, now_dt: datetime.datetime) -> datetime.date:
        """Get the effective liturgical date, considering First Vespers (4:00 PM)."""
        today = now_dt.date()
        
        # Sundays and Solemnities begin at 4:00 PM (16:00) the evening before
        if now_dt.hour >= 16:
            tomorrow = today + datetime.timedelta(days=1)
            tomorrow_key = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
            
            # Check tomorrow's festivities in our cache
            tomorrow_festivities = self.festivities.get(tomorrow_key, [])
            for festivity in tomorrow_festivities:
                grade = festivity.get("liturgical_grade", 0)
                # Solemnities (6+) or any Sunday (tomorrow.weekday() == 6)
                if grade >= 6 or tomorrow.weekday() == 6:
                    _LOGGER.debug("First Vespers active: Switching to tomorrow's observance early")
                    return tomorrow
                    
        return today

    def get_season_for_date(self, date: datetime.date) -> LiturgicalSeason:
        """Get the liturgical season for a specific date."""
        gen = CalendarGenerator(date.year)
        return gen.get_season(date)

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

        # Prune old festivities
        cutoff = datetime.datetime(today.year - 1, today.month, today.day)
        self.festivities = {
            k: v for k, v in self.festivities.items() if k >= cutoff
        }
        self.years_loaded = {y for y in self.years_loaded if y >= today.year - 1}

        return {
            "all_festivities": self.festivities,
        }
