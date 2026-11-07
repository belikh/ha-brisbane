"""Binary sensors for City of Brisbane."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BrisbaneCoordinator
from .const import DOMAIN, MODE_WASTE
from .waste import put_out_tonight, recycle_out_tonight_bcc


class BrisbaneWastePutOutTonightSensor(
    CoordinatorEntity[BrisbaneCoordinator], BinarySensorEntity
):
    """True when bins go out tonight for tomorrow's collection."""

    _attr_has_entity_name = True
    _attr_name = "Put bins out tonight"
    _attr_unique_id = "brisbane_waste_put_out_tonight"

    def __init__(self, coordinator: BrisbaneCoordinator) -> None:
        """Initialise the binary sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Brisbane",
            manufacturer="belikh",
            model="Brisbane Integration",
            configuration_url="https://github.com/belikh/ha-brisbane",
        )

    @property
    def is_on(self) -> bool:
        """Return whether bins go out tonight."""
        waste = self.coordinator.waste or {}
        bin_day = str(waste.get("collection_day") or "")
        try:
            from zoneinfo import ZoneInfo

            today = datetime.now(ZoneInfo("Australia/Brisbane")).date()
        except Exception:  # noqa: BLE001 - fallback to UTC date
            today = datetime.now().date()
        return put_out_tonight(bin_day, today)

    @property
    def extra_state_attributes(self) -> dict:
        """Return waste details."""
        waste = self.coordinator.waste or {}
        return {
            "address": waste.get("property_id"),
            "bin_day": waste.get("collection_day"),
            "recycle_week": waste.get("zone"),
        }


class BrisbaneWasteRecycleTonightSensor(
    CoordinatorEntity[BrisbaneCoordinator], BinarySensorEntity
):
    """True when recycling goes out tonight (BCC weeks)."""

    _attr_has_entity_name = True
    _attr_name = "Recycling out tonight"
    _attr_unique_id = "brisbane_waste_recycle_tonight"

    def __init__(self, coordinator: BrisbaneCoordinator) -> None:
        """Initialise the binary sensor."""
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool:
        """Return whether recycling goes out tonight."""
        waste = self.coordinator.waste or {}
        bin_day = str(waste.get("collection_day") or "")
        try:
            from zoneinfo import ZoneInfo

            today = datetime.now(ZoneInfo("Australia/Brisbane")).date()
        except Exception:  # noqa: BLE001 - fallback to UTC date
            today = datetime.now().date()
        return recycle_out_tonight_bcc(bin_day, self.coordinator.week_starts, today)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Brisbane binary sensors from a config entry."""
    coordinator: BrisbaneCoordinator = hass.data["brisbane"][entry.entry_id]
    if coordinator.mode != MODE_WASTE:
        return
    async_add_entities(
        [
            BrisbaneWastePutOutTonightSensor(coordinator),
            BrisbaneWasteRecycleTonightSensor(coordinator),
        ]
    )
