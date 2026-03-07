"""Catholic Calendar integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .coordinator import CatholicCalendarCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "catholic_calendar"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR]

CONFIG_SCHEMA = cv.platform_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Catholic Calendar component (legacy YAML support)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Catholic Calendar from a config entry."""
    _LOGGER.debug("Setting up Catholic Calendar from config entry")

    coordinator = CatholicCalendarCoordinator(hass, config_entry=entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_get_coordinator(
    hass: HomeAssistant, entry_id: str | None = None
) -> CatholicCalendarCoordinator:
    """Get the shared coordinator (used by platform setup)."""
    if entry_id and entry_id in hass.data[DOMAIN]:
        return hass.data[DOMAIN][entry_id]

    # Fallback for legacy setups
    if "coordinator" not in hass.data[DOMAIN]:
        # Legacy setup doesn't have a config_entry
        coordinator = CatholicCalendarCoordinator(hass, config_entry=None)
        hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator
        await coordinator.async_config_entry_first_refresh()

    return hass.data[DOMAIN]["coordinator"]
