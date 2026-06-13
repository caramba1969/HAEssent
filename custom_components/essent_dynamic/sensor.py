"""Sensor platform for Essent Dynamic Pricing."""
import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import EssentDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        EssentCurrentPriceSensor(coordinator, "electricity", "Current Electricity Price", "mdi:flash", "EUR/kWh"),
        EssentDailyStatSensor(coordinator, "electricity", "average", "Average Electricity Price Today", "mdi:chart-bell-curve", "EUR/kWh"),
        EssentDailyStatSensor(coordinator, "electricity", "min", "Min Electricity Price Today", "mdi:arrow-down-bold-circle-outline", "EUR/kWh"),
        EssentDailyStatSensor(coordinator, "electricity", "max", "Max Electricity Price Today", "mdi:arrow-up-bold-circle-outline", "EUR/kWh"),

        EssentCurrentPriceSensor(coordinator, "gas", "Current Gas Price", "mdi:fire", "EUR/m³"),
        EssentDailyStatSensor(coordinator, "gas", "average", "Average Gas Price Today", "mdi:chart-bell-curve", "EUR/m³"),
        EssentDailyStatSensor(coordinator, "gas", "min", "Min Gas Price Today", "mdi:arrow-down-bold-circle-outline", "EUR/m³"),
        EssentDailyStatSensor(coordinator, "gas", "max", "Max Gas Price Today", "mdi:arrow-up-bold-circle-outline", "EUR/m³"),
    ]
    async_add_entities(sensors)


class EssentCurrentPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Essent Dynamic Price sensor."""

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
        name: str,
        icon: str,
        unit: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._energy_type = energy_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"essent_dynamic_{energy_type}_price"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        if not self.coordinator.data or not self.coordinator.data.get(self._energy_type):
            return None

        now = dt_util.now()
        
        for tariff in self.coordinator.data[self._energy_type]["tariffs"]:
            start_str = tariff.get("startDateTime")
            end_str = tariff.get("endDateTime")
            if not start_str or not end_str:
                continue

            try:
                # API returns strings like "2026-06-12T00:00:00"
                start_dt = dt_util.parse_datetime(start_str)
                end_dt = dt_util.parse_datetime(end_str)

                # Ensure tzinfo is set, assume local timezone if none provided by API
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

                if start_dt <= now < end_dt:
                    return tariff.get("totalAmount")
            except Exception as e:
                _LOGGER.debug("Error parsing dates for %s: %s", self._energy_type, e)
                
        return None

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get(self._energy_type):
            return {}

        today_prices = []
        tomorrow_prices = []
        
        now = dt_util.now()
        today = now.date()
        tomorrow = dt_util.now().date() + timedelta(days=1)

        for tariff in self.coordinator.data[self._energy_type]["tariffs"]:
            start_str = tariff.get("startDateTime")
            end_str = tariff.get("endDateTime")
            if not start_str or not end_str:
                continue

            try:
                start_dt = dt_util.parse_datetime(start_str)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                    
                tariff_date = start_dt.date()
                price_data = {
                    "start": start_dt.isoformat(),
                    "end": dt_util.parse_datetime(end_str).replace(tzinfo=dt_util.DEFAULT_TIME_ZONE).isoformat() if dt_util.parse_datetime(end_str).tzinfo is None else dt_util.parse_datetime(end_str).isoformat(),
                    "price": tariff.get("totalAmount")
                }
                
                if tariff_date == today:
                    today_prices.append(price_data)
                elif tariff_date == tomorrow:
                    tomorrow_prices.append(price_data)

            except Exception as e:
                pass

        attrs = {
            "today": today_prices,
            "tomorrow": tomorrow_prices
        }
        
        # Add min, average, max for today and tomorrow
        days_data = self.coordinator.data[self._energy_type].get("days", {})
        today_str = today.isoformat()
        tomorrow_str = tomorrow.isoformat()
        
        if today_str in days_data:
            attrs["average_price_today"] = days_data[today_str].get("average")
            attrs["min_price_today"] = days_data[today_str].get("min")
            attrs["max_price_today"] = days_data[today_str].get("max")
            
        if tomorrow_str in days_data:
            attrs["average_price_tomorrow"] = days_data[tomorrow_str].get("average")
            attrs["min_price_tomorrow"] = days_data[tomorrow_str].get("min")
            attrs["max_price_tomorrow"] = days_data[tomorrow_str].get("max")

        return attrs

class EssentDailyStatSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Essent Daily Stat sensor."""

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
        stat_type: str,
        name: str,
        icon: str,
        unit: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._energy_type = energy_type
        self._stat_type = stat_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"essent_dynamic_{energy_type}_{stat_type}_price"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the requested stat for today."""
        if not self.coordinator.data or not self.coordinator.data.get(self._energy_type):
            return None

        today_str = dt_util.now().date().isoformat()
        days_data = self.coordinator.data[self._energy_type].get("days", {})
        
        if today_str in days_data:
            return days_data[today_str].get(self._stat_type)
            
        return None
