# Brisbane City Council

Home Assistant integration for **Brisbane City Council** — Queensland, Australia.

Everything in here comes from the council's public open data
(token-free, no API keys, no add-ons).

## What you get

- **All datasets** — every published dataset becomes a sensor showing its resource/feature count and source URL.
- **Waste collection days** (where openly published) — next bin collection + "put bins out tonight?" for one address/property.

## Data source

Huwise Explore API (448 datasets, CC BY 4.0, token-free). Waste uses the Waste Collection Days dataset (property_id, collection_day, zone).

## Install (HACS)

1. Add a custom repository: `https://github.com/belikh/ha-brisbane` as type **Integration**.
2. Install **Brisbane City Council** and restart Home Assistant.
3. Add the integration and choose: all layers / waste / single layer.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

Licence: MIT. Data © Brisbane City Council (Creative Commons). Unofficial; not endorsed by the council.
