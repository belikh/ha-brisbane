"""Constants for the Brisbane integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "brisbane"

CONF_MODE = "mode"
CONF_ADDRESS = "address"
CONF_LAYER_TITLE = "layer_title"
CONF_SCAN_INTERVAL = "scan_interval_hours"

MODE_ALL_LAYERS = "all_layers"
MODE_WASTE = "waste"
MODE_SINGLE_LAYER = "single_layer"

CATALOGUE_URL = (
    "https://data.brisbane.qld.gov.au/api/explore/v2.1/catalog/datasets"
)
WASTE_DATASET_ID = "waste-collection-days-collection-days"

DEFAULT_SCAN_INTERVAL = timedelta(hours=6)
MIN_SCAN_INTERVAL_HOURS = 1
MAX_SCAN_INTERVAL_HOURS = 48

ATTR_LAYER_TITLE = "layer_title"
ATTR_FEATURE_COUNT = "feature_count"
ATTR_SOURCE_URL = "source_url"
ATTR_LAST_UPDATED = "last_updated"
