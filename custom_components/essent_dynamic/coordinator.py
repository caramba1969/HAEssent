"""DataUpdateCoordinator for Essent Dynamic Pricing."""
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class EssentDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Essent data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Essent API."""
        headers = {
            "Accept": "application/json",
            "x-request-origin": "client",
        }
        try:
            async with async_timeout.timeout(30):
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL, headers=headers) as response:
                        response.raise_for_status()
                        data = await response.json()
                        return self._parse_data(data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    def _parse_data(self, data: dict) -> dict[str, Any]:
        """Parse the API response into a more usable format."""
        parsed = {
            "electricity": [],
            "gas": [],
        }

        # The API returns a list of days in 'prices'
        prices_by_day = data.get("prices", [])
        
        for day in prices_by_day:
            if "electricity" in day and "tariffs" in day["electricity"]:
                parsed["electricity"].extend(day["electricity"]["tariffs"])
            if "gas" in day and "tariffs" in day["gas"]:
                parsed["gas"].extend(day["gas"]["tariffs"])

        return parsed
