"""Catholic Calendar integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .coordinator import CatholicCalendarCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "catholic_calendar"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Catholic Calendar component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize and refresh the coordinator here once
    if "coordinator" not in hass.data[DOMAIN]:
        _LOGGER.debug("Initializing Catholic Calendar Coordinator")
        coordinator = CatholicCalendarCoordinator(hass)
        hass.data[DOMAIN]["coordinator"] = coordinator
        await coordinator.async_config_entry_first_refresh()
    
    return True


async def async_get_coordinator(hass: HomeAssistant) -> CatholicCalendarCoordinator:
    """Get the shared coordinator."""
    if DOMAIN not in hass.data or "coordinator" not in hass.data[DOMAIN]:
        # This case should be handled by async_setup, but adding for robustness
        _LOGGER.debug("Initializing Catholic Calendar Coordinator from getter")
        coordinator = CatholicCalendarCoordinator(hass)
        hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator
        await coordinator.async_config_entry_first_refresh()

    return hass.data[DOMAIN]["coordinator"]
