"""Catholic Calendar sensor."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as BASE_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import async_get_coordinator
from .coordinator import CatholicCalendarCoordinator
from .liturgical_season import LiturgicalSeason

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
    """Set up the Catholic Calendar sensor from YAML."""
    name = config[CONF_NAME]
    coordinator = await async_get_coordinator(hass)

    async_add_devices(
        [
            CatholicCalendarSensor(coordinator, name),
            CatholicCalendarSeasonSensor(coordinator, name),
        ],
    )


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
            CatholicCalendarSensor(coordinator, name),
            CatholicCalendarSeasonSensor(coordinator, name),
        ],
    )


class CatholicCalendarSensor(
    CoordinatorEntity[CatholicCalendarCoordinator], SensorEntity
):
    """Representation of a Catholic Calendar sensor."""

    _attr_force_update = True
    _attr_has_entity_name = True
    _attr_translation_key = "roman_catholic_today"
    _attr_icon = "mdi:calendar"

    def __init__(
        self,
        coordinator: CatholicCalendarCoordinator,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        name_slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{name_slug}_today"
        self._attr_name = "Today"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name_slug)},
            name=name,
            manufacturer="Roman Catholic Church",
            model="Western Liturgical Calendar",
            sw_version=__version__,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data["today"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "season": self.coordinator.data["season"],
            "festivities": self.coordinator.data["festivities"],
        }


class CatholicCalendarSeasonSensor(
    CoordinatorEntity[CatholicCalendarCoordinator], SensorEntity
):
    """Representation of a Catholic Calendar Season sensor."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [season.value for season in LiturgicalSeason]
    _attr_icon = "mdi:church"
    _attr_has_entity_name = True
    _attr_translation_key = "roman_catholic_liturgical_season"

    def __init__(self, coordinator: CatholicCalendarCoordinator, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        name_slug = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{name_slug}_liturgical_season"
        self._attr_name = "Liturgical Season"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name_slug)},
            name=name,
            manufacturer="Roman Catholic Church",
            model="Western Liturgical Calendar",
            sw_version=__version__,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data["season"]
