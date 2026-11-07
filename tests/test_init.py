"""Tests for the Brisbane integration."""

from datetime import date

from custom_components.brisbane.client import (
    build_waste_where,
    parse_catalogue,
    parse_waste_property,
)
from custom_components.brisbane.waste import next_collection_date, put_out_tonight

CATALOGUE_FIXTURE = {
    "results": [
        {
            "dataset_id": "waste-collection-days-collection-days",
            "metas": {"default": {"title": "Waste Collection Days"}},
        },
        {
            "dataset_id": "traffic-data-at-intersection",
            "metas": {"default": {"title": "Traffic Management — Intersection volume"}},
        },
    ]
}

WASTE_FIXTURE = {
    "results": [
        {
            "property_id": "1123752",
            "house_number": "35",
            "street_name": "PEEL ST",
            "suburb": "SOUTH BRISBANE",
            "collection_day": "THURSDAY",
            "zone": "ZONE 1",
        }
    ]
}


def test_parse_catalogue_skips_empty_and_sorts() -> None:
    layers = parse_catalogue(CATALOGUE_FIXTURE)
    assert len(layers) == 2
    assert layers[0].title == "Traffic Management — Intersection volume"
    assert layers[1].title == "Waste Collection Days"


def test_build_waste_where() -> None:
    assert build_waste_where("1123752") == 'property_id="1123752"'


def test_parse_waste_property() -> None:
    result = parse_waste_property(WASTE_FIXTURE)
    assert result is not None
    assert result["collection_day"] == "THURSDAY"
    assert parse_waste_property({"results": []}) is None


def test_next_collection_date() -> None:
    assert next_collection_date("tuesday", date(2026, 11, 7)) == date(2026, 11, 10)
    assert next_collection_date("SATURDAY", date(2026, 11, 7)) == date(2026, 11, 7)
    assert next_collection_date("BOGUS", date(2026, 11, 7)) is None


def test_put_out_tonight() -> None:
    assert put_out_tonight("TUESDAY", date(2026, 11, 9)) is True
    assert put_out_tonight("TUESDAY", date(2026, 11, 8)) is False
