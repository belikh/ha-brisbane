"""Calendar entity for Brisbane waste collections."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BrisbaneCoordinator
from .const import DOMAIN, MODE_WASTE
from .waste import next_collection_date


class BrisbaneCollectionsCalendar(
    CoordinatorEntity[BrisbaneCoordinator], CalendarEntity
):
    """Calendar of Brisbane waste collections."""

    _attr_has_entity_name = True
    _attr_name = "Collections"
    _attr_unique_id = "brisbane_collections_calendar"
    _attr_device_info = DeviceInfo(
        identifiers={(DOMAIN, DOMAIN)},
        name="Brisbane City Council",
        manufacturer="belikh",
        model="Brisbane Integration",
        configuration_url="https://github.com/belikh/ha-brisbane",
    )

    def __init__(self, coordinator: BrisbaneCoordinator) -> None:
        """Initialise the calendar entity."""
        super().__init__(coordinator)

    @property
    def active(self) -> bool:
        """Return whether any collection happens tomorrow."""
        return False

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return upcoming collection events (next 4 weeks)."""
        waste = self.coordinator.waste or {}
        bin_day = str(waste.get("collection_day") or "")
        if not bin_day:
            return []
        week_starts = self.coordinator.week_starts or []
        events: list[CalendarEvent] = []
        cursor = start_date.date()
        end = end_date.date()
        while cursor <= end:
            nxt = next_collection_date(bin_day, cursor)
            if nxt is None or nxt > end:
                break
            in_recycle = any(ws <= nxt <= ws + timedelta(days=6) for ws in week_starts)
            summary = "General waste" + (
                " + recycling" if in_recycle else " + organics"
            )
            events.append(
                CalendarEvent(
                    summary=summary,
                    start=nxt,
                    end=nxt + timedelta(days=1),
                    description=f"Bin day {bin_day.lower()} (zone {waste.get('zone')})",
                )
            )
            cursor = nxt + timedelta(days=7)
        return events


async def async_setup_entry(
    hass: HomeAssistant,
    entry: object,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brisbane calendar."""
    assert hasattr(entry, "entry_id")
    coordinator: BrisbaneCoordinator = hass.data[DOMAIN][entry.entry_id]  # type: ignore[index]
    if coordinator.mode != MODE_WASTE:
        return
    async_add_entities([BrisbaneCollectionsCalendar(coordinator)])
