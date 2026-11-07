"""Huwise Explore API client for Brisbane City Council.

Every endpoint here is token-free. Brisbane Open Data runs on the
Huwise (formerly Opendatasoft) platform; datasets are queried with
the standard Explore API ``/records`` operation. Licence: CC BY 4.0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientSession

from .const import CATALOGUE_URL, WASTE_DATASET_ID


@dataclass(frozen=True)
class LayerDefinition:
    """One published Brisbane Open Data dataset."""

    title: str
    url: str
    description: str = ""
    categories: tuple[str, ...] = ()


@dataclass
class CatalogueResult:
    """Result of a catalogue fetch."""

    layers: list[LayerDefinition] = field(default_factory=list)


DYNAMIC_TITLE_SUBSTRINGS = (
    "waste collection",
    "bin collection",
    "large item collection",
    "intersection volume",
    "rainfall",
    "stream height",
    "pedestrian movement",
    "bikeway counts",
    "events",
    "planned temporary road occupancies",
    "enterococci monitoring results",
    "work schedules",
    "enquiries",
    "trip numbers",
    "occupancy forecasting",
)


def is_junk_title(title: str) -> bool:
    """Return True if a dataset is not dynamic (kept whitelist) or historical."""
    lowered = title.lower()
    if "historical" in lowered:
        return True
    return not any(token in lowered for token in DYNAMIC_TITLE_SUBSTRINGS)


def parse_catalogue(payload: dict[str, Any]) -> list[LayerDefinition]:
    """Parse an Explore API catalogue payload into layers.

    Pure function (no I/O) so it can be unit-tested with fixtures.
    """
    layers: list[LayerDefinition] = []
    results = payload.get("results") or []
    for item in results:
        dataset_id = str(item.get("dataset_id") or "").strip()
        metas = (item.get("metas") or {}).get("default") or {}
        title = str(metas.get("title") or dataset_id).strip()
        if not dataset_id:
            continue
        if is_junk_title(title):
            continue
        description = str(metas.get("description") or "").strip()
        raw_theme = metas.get("theme") or []
        categories = (
            tuple(str(c) for c in raw_theme if c) if isinstance(raw_theme, list) else ()
        )
        layers.append(
            LayerDefinition(
                title=title,
                url=f"{CATALOGUE_URL}/{dataset_id}",
                description=description,
                categories=categories,
            )
        )
    layers.sort(key=lambda item: item.title.lower())
    return layers


def parse_waste_property(
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Extract the first waste property from an Explore records response."""
    results = payload.get("results") or []
    if not results:
        return None
    return dict(results[0])


def build_waste_where(property_id: str) -> str:
    """Build an Explore WHERE clause for one property_id."""
    escaped = property_id.replace('"', '""').strip()
    return f'property_id="{escaped}"'


class BrisbaneClient:
    """Thin async client for Brisbane Open Data."""

    def __init__(self, session: ClientSession) -> None:
        """Initialise with a shared aiohttp session."""
        self._session = session

    async def fetch_catalogue(self) -> list[LayerDefinition]:
        """Fetch and parse the dataset catalogue."""
        async with self._session.get(
            CATALOGUE_URL, params={"limit": "1000"}
        ) as response:
            response.raise_for_status()
            payload = await response.json()
        return parse_catalogue(payload)

    async def query_layer_count(self, definition: LayerDefinition) -> int:
        """Return the record count for one dataset (best effort)."""
        dataset_id = definition.url.rstrip("/").split("/")[-1]
        async with self._session.get(
            f"{CATALOGUE_URL}/{dataset_id}/records",
            params={"limit": "0"},
        ) as response:
            response.raise_for_status()
            payload = await response.json()
        count = payload.get("total_count")
        return int(count) if isinstance(count, (int, float)) else 0

    async def fetch_telemetry_latest(self) -> dict[str, Any] | None:
        """Fetch the latest telemetry record (status snapshot)."""
        url = f"{CATALOGUE_URL}/telemetry-sensors-rainfall-and-stream-heights/records"
        async with self._session.get(
            url,
            params={"limit": "1", "sort": "-measured"},
        ) as response:
            response.raise_for_status()
            return parse_waste_property(await response.json())

    async def fetch_intersection_latest(self) -> dict[str, Any] | None:
        """Fetch the latest intersection traffic record."""
        url = f"{CATALOGUE_URL}/traffic-data-at-intersection/records"
        async with self._session.get(
            url,
            params={"limit": "1", "sort": "-recorded"},
        ) as response:
            response.raise_for_status()
            return parse_waste_property(await response.json())

    async def fetch_next_event(self) -> dict[str, Any] | None:
        """Fetch the next council event (soonest first)."""
        url = f"{CATALOGUE_URL}/brisbane-city-council-events/records"
        async with self._session.get(
            url,
            params={"limit": "1", "sort": "start_datetime"},
        ) as response:
            response.raise_for_status()
            return parse_waste_property(await response.json())

    async def fetch_waste_property(self, property_id: str) -> dict[str, Any] | None:
        """Fetch collection day / zone for one property_id."""
        url = f"{CATALOGUE_URL}/{WASTE_DATASET_ID}/records"
        async with self._session.get(
            url,
            params={
                "where": build_waste_where(property_id),
                "limit": "1",
            },
        ) as response:
            response.raise_for_status()
            payload = await response.json()
        return parse_waste_property(payload)
