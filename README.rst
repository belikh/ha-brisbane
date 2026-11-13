.. raw:: html

   <p align="right">
     <picture>
       <source media="(prefers-color-scheme: dark)" srcset="https://github.com/belikh/design/releases/latest/download/logo-dark.svg">
       <img alt="jupiter.au" src="https://github.com/belikh/design/releases/latest/download/logo-light.svg" width="260">
     </picture>
   </p>

   <h1>Brisbane City Council</h1>

.. meta::
   :description: Home Assistant integration that turns datasets from the Brisbane City Council open data portal into sensors.

Home Assistant integration that turns datasets from the Brisbane City Council open data portal into sensors. It needs no API key.

|

.. raw:: html

   <p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/belikh/design/releases/latest/download/rule-end-dark.svg"><img alt="" src="https://github.com/belikh/design/releases/latest/download/rule-end-light.svg" width="50%"></picture></p>

Install
-------

1. In HACS, add a custom repository: ``https://github.com/belikh/ha-brisbane``, type **Integration**.
2. Install **Brisbane City Council** and restart Home Assistant.
3. Go to **Settings > Devices & Services > Add integration** and pick **Brisbane City Council**.

|

Use
---

The integration reads the council's catalogue from ``data.brisbane.qld.gov.au`` (Huwise Explore API) and creates one sensor per dataset. The state is the number of records in the dataset. The attributes are ``layer_title``, ``source_url`` and ``feature_count``.

The catalogue is filtered to datasets that change over time. Datasets whose titles do not match the integration's list of live-data keywords, and historical datasets, are skipped.

|

Configuration
-------------

The refresh interval is set at setup and can be changed later under **Configure** on the integration card. It defaults to 6 hours and accepts 1 to 48.

|

Develop
-------

.. code-block:: sh

   uv sync
   uv run pytest
   uv run ruff check .
   uv run mypy

|

.. raw:: html

   <p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/belikh/design/releases/latest/download/rule-end-dark.svg"><img alt="" src="https://github.com/belikh/design/releases/latest/download/rule-end-light.svg" width="50%"></picture></p>

Licence
-------

MIT. Data (c) Brisbane City Council, CC BY 4.0. Unofficial; not endorsed by the council.

|

.. raw:: html

   <p align="right"><sub>jupiter.au</sub></p>

