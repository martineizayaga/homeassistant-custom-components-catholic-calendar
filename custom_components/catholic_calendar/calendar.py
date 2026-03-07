"""Catholic Calendar calendar."""

from __future__ import annotations

import datetime
import logging

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import async_get_coordinator
from .coordinator import CatholicCalendarCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)

__version__ = "2.0.1"
DOMAIN = "catholic_calendar"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Catholic Calendar sensor from a config entry."""
    name = entry.data[CONF_NAME]
    coordinator = await async_get_coordinator(hass, entry.entry_id)

    async_add_entities(
        [
            CatholicCalendar(coordinator, name),
        ],
    )


class CatholicCalendar(CoordinatorEntity[CatholicCalendarCoordinator], CalendarEntity):
    """Representation of a Catholic Calendar calendar."""

    _attr_force_update = True
    _attr_has_entity_name = True
    _attr_translation_key = "roman_catholic_calendar"

    def __init__(
        self,
        coordinator: CatholicCalendarCoordinator,
        name: str,
    ) -> None:
        """Initialize the calendar."""
        super().__init__(coordinator)
        name_slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{name_slug}_calendar"
        self._attr_name = "Calendar"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name_slug)},
            name=name,
            manufacturer="Roman Catholic Church",
            model="Western Liturgical Calendar",
            sw_version=__version__,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        active_date = self.coordinator.get_liturgical_date(dt_util.now())
        events = self.__get_calendar_events(active_date)
        if len(events) == 0:
            return None
        return events[0]

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        calendar_events = []
        all_festivities = self.coordinator.data["all_festivities"]

        curr_date = start_date
        while curr_date <= end_date:
            date_key = datetime.datetime(curr_date.year, curr_date.month, curr_date.day)
            if date_key in all_festivities:
                for festivity in sorted(
                    all_festivities[date_key],
                    key=lambda x: x.get("liturgical_grade", 0),
                    reverse=True,
                ):
                    calendar_events.append(
                        CalendarEvent(
                            start=date_key.date(),
                            end=date_key.date() + datetime.timedelta(days=1),
                            summary=festivity["name"],
                            description=(
                                f"liturgical_color: {festivity['liturgical_color']}, "
                                "liturgical_grade: "
                                f"{festivity['liturgical_grade_desc']}"
                            ),
                        )
                    )
            curr_date += datetime.timedelta(days=1)

        return calendar_events

    def __get_calendar_events(self, date: datetime.date) -> list[CalendarEvent]:
        """Get events for a specific date."""
        calendar_events = []
        all_festivities = self.coordinator.data["all_festivities"]
        date_key = datetime.datetime(date.year, date.month, date.day)

        if date_key in all_festivities:
            for festivity in sorted(
                all_festivities[date_key],
                key=lambda x: x.get("liturgical_grade", 0),
                reverse=True,
            ):
                calendar_events.append(
                    CalendarEvent(
                        start=date,
                        end=date + datetime.timedelta(days=1),
                        summary=festivity["name"],
                        description=(
                            f"liturgical_color: {festivity['liturgical_color']}, "
                            "liturgical_grade: "
                            f"{festivity['liturgical_grade_desc']}"
                        ),
                    )
                )
        return calendar_events
