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


JUNK_TITLE_SUBSTRINGS = (
    "superseded",
    "city plan",
    "planning scheme",
)


def is_junk_title(title: str) -> bool:
    """Return True if a dataset is superseded/static planning junk."""
    lowered = title.lower()
    return any(token in lowered for token in JUNK_TITLE_SUBSTRINGS)


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
            tuple(str(c) for c in raw_theme if c)
            if isinstance(raw_theme, list)
            else ()
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

    async def fetch_waste_property(
        self, property_id: str
    ) -> dict[str, Any] | None:
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
