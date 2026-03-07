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
        self, hass: HomeAssistant, config_entry: ConfigEntry | None = None
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

        if now_dt.hour >= 16:
            tomorrow = today + datetime.timedelta(days=1)
            tomorrow_key = datetime.datetime(
                tomorrow.year, tomorrow.month, tomorrow.day
            )

            tomorrow_festivities = self.festivities.get(tomorrow_key, [])
            for festivity in tomorrow_festivities:
                grade = festivity.get("liturgical_grade", 0)
                if grade >= 6 or tomorrow.weekday() == 6:
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
        years_to_load = [today.year, today.year + 1]

        for year in years_to_load:
            if year not in self.years_loaded:
                _LOGGER.debug("Generating festivities for year %s", year)
                gen = CalendarGenerator(year)
                year_festivities = gen.generate_festivities()

                for date_key, events in year_festivities.items():
                    if date_key not in self.festivities:
                        self._process_date_events(date_key, events, gen)

                self.years_loaded.add(year)

        # Prune old festivities
        cutoff = datetime.datetime(today.year - 1, today.month, today.day)
        self.festivities = {k: v for k, v in self.festivities.items() if k >= cutoff}
        self.years_loaded = {y for y in self.years_loaded if y >= today.year - 1}

        # Sort by Liturgical Grade
        for date_key in self.festivities:
            self.festivities[date_key].sort(
                key=lambda x: x.get("liturgical_grade", 0), reverse=True
            )

        return {"all_festivities": self.festivities}

    def _process_date_events(
        self,
        date_key: datetime.datetime,
        events: list[dict[str, Any]],
        gen: CalendarGenerator,
    ) -> None:
        """Enrich and filter events for a specific date."""
        self.festivities[date_key] = []
        dt = date_key.date()
        season = gen.get_season(dt)

        # --- GIRM No. 373: US Adaptation Penance Day ---
        if dt.month == 1 and dt.day == 22:
            self.festivities[date_key].append(
                {
                    "name": "Prayer for the Legal Protection of Unborn Children",
                    "liturgical_color": "violet",
                    "liturgical_grade": LiturgicalGrade.COMMEMORATION,
                    "liturgical_grade_desc": "Day of Penance (USA)",
                }
            )

        for event in events:
            enriched_event = dict(event)
            grade = enriched_event.get("liturgical_grade", 0)

            if enriched_event.get("liturgical_color") == "pink":
                enriched_event["liturgical_color"] = "rose"

            # --- GIRM No. 355 Rules ---
            is_holy_week = (
                enriched_event["name"] == "Ash Wednesday"
                or "Holy Week" in enriched_event["name"]
            )
            is_late_advent = dt.month == 12 and 17 <= dt.day <= 24
            is_octave = (dt.month == 12 and dt.day >= 26) or (
                dt.month == 1 and dt.day <= 5
            )

            # Combined boolean for privileged seasons
            is_privileged = (
                season == LiturgicalSeason.LENT or is_late_advent or is_octave
            )

            if is_holy_week and grade <= LiturgicalGrade.MEMORIAL:
                continue

            if is_privileged and grade == LiturgicalGrade.MEMORIAL:
                grade = LiturgicalGrade.COMMEMORATION
                enriched_event["liturgical_grade"] = grade

            enriched_event["liturgical_grade_desc"] = (
                LiturgicalGrade.descr(int(grade)) or "Unknown"
            )
            self.festivities[date_key].append(enriched_event)
