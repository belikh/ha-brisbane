"""Sensors for City of Brisbane."""

from __future__ import annotations

from datetime import UTC, date, datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BrisbaneCoordinator
from .const import MODE_WASTE
from .waste import next_collection_date

EPOCH = date(2026, 1, 5)


class BrisbaneLayerSensor(
    CoordinatorEntity[BrisbaneCoordinator], SensorEntity
):
    """Sensor exposing the feature count for one Datahub layer."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BrisbaneCoordinator,
        layer_title: str,
        source_url: str,
    ) -> None:
        """Initialise with the layer title and source URL."""
        super().__init__(coordinator)
        self._layer_title = layer_title
        self._source_url = source_url
        slug = layer_title.lower().replace(" ", "_")
        self._attr_unique_id = f"{layer_title}_{slug}"
        self._attr_name = layer_title
        self._attr_native_unit_of_measurement = "features"

    @property
    def native_value(self) -> int | None:
        """Return the feature count for this layer."""
        return self.coordinator.counts.get(self._layer_title)

    @property
    def extra_state_attributes(self) -> dict:
        """Return layer metadata."""
        return {
            "layer_title": self._layer_title,
            "source_url": self._source_url,
            "feature_count": self.coordinator.counts.get(self._layer_title),
        }


class BrisbaneWasteNextCollectionSensor(
    CoordinatorEntity[BrisbaneCoordinator], SensorEntity
):
    """Sensor for the next bin collection date."""

    _attr_has_entity_name = True
    _attr_device_class = None
    _attr_name = "Next bin collection"
    _attr_unique_id = "brisbane_waste_next_collection"

    def __init__(self, coordinator: BrisbaneCoordinator) -> None:
        """Initialise the waste sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> str | None:
        """Return the next collection date as ISO text."""
        waste = self.coordinator.waste or {}
        bin_day = str(waste.get("collection_day") or "")
        today = datetime.now(UTC).date()
        try:
            from zoneinfo import ZoneInfo

            today = datetime.now(ZoneInfo("Australia/Brisbane")).date()
        except Exception:  # noqa: BLE001 - fallback to UTC date
            pass
        nxt = next_collection_date(bin_day, today)
        return nxt.isoformat() if nxt else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return waste details."""
        waste = self.coordinator.waste or {}
        return {
            "address": waste.get("property_id"),
            "bin_day": waste.get("collection_day"),
            "recycle_week": waste.get("zone"),
            "suburb": waste.get("suburb"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Brisbane sensors from a config entry."""
    coordinator: BrisbaneCoordinator = hass.data["brisbane"][entry.entry_id]
    entities: list[SensorEntity] = []
    for layer in coordinator.layers:
        entities.append(
            BrisbaneLayerSensor(coordinator, layer.title, layer.url)
        )
    if coordinator.mode == MODE_WASTE:
        entities.append(BrisbaneWasteNextCollectionSensor(coordinator))
    async_add_entities(entities)
