"""Global fixtures for Catholic Calendar tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.catholic_calendar.coordinator import CatholicCalendarCoordinator

@pytest.fixture
def hass() -> HomeAssistant:
    """Mock Home Assistant instance."""
    hass_mock = MagicMock(spec=HomeAssistant)
    # Mock the executor job to just run the function immediately
    hass_mock.async_add_executor_job = lambda func, *args: func(*args)
    return hass_mock

@pytest.fixture
def coordinator(hass: HomeAssistant) -> CatholicCalendarCoordinator:
    """Fixture for CatholicCalendarCoordinator."""
    return CatholicCalendarCoordinator(hass, config_entry=None)
