"""Catholic Calendar calendar."""

from __future__ import annotations

import datetime
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.calendar import (
    PLATFORM_SCHEMA as BASE_SCHEMA,
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import async_get_coordinator
from .coordinator import CatholicCalendarCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)

__version__ = "1.1.0"
DOMAIN = "catholic_calendar"

PLATFORM_SCHEMA = BASE_SCHEMA.extend(
    {vol.Required(CONF_NAME): cv.string},
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Catholic Calendar sensor."""
    name = config[CONF_NAME]
    
    coordinator = await async_get_coordinator(hass)
    
    async_add_devices(
        [
            CatholicCalendar(coordinator, name),
        ],
    )


class CatholicCalendar(CoordinatorEntity[CatholicCalendarCoordinator], CalendarEntity):
    """Representation of a Catholic Calendar calendar."""

    _attr_force_update = True
    _attr_has_entity_name = True

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
            identifiers={(DOMAIN, name)},
            name=name,
            manufacturer="Roman Catholic Church",
            model="Western Liturgical Calendar",
            sw_version=__version__,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        today = self.coordinator.data["today"]
        events = self.__get_calendar_events(today)
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
                            end=date_key.date(),
                            summary=festivity["name"],
                            description=(
                                f"liturgical_color: {festivity['liturgical_color']}, "
                                f"liturgical_grade: {festivity['liturgical_grade_desc']}"
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
                        end=date,
                        summary=festivity["name"],
                        description=(
                            f"liturgical_color: {festivity['liturgical_color']}, "
                            f"liturgical_grade: {festivity['liturgical_grade_desc']}"
                        ),
                    )
                )
        return calendar_events
