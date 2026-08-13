# HellasCube

A geospatial satellite data analysis platform for Greece, built on [Open Data Cube (ODC)](https://www.opendatacube.org/). HellasCube enables environmental monitoring and spectral index analysis over Greek territory using Sentinel-2 L2A and Landsat 8 imagery.

Developed as a thesis project at the International Hellenic University.

---

## Overview

HellasCube is a system for the analyzation of geographic data, provided by satelite missions such as Sentinel-2 and Landsat. The data are being analyzed with the help of Open Data Cube. The datasets form the satelites are being locally saved as indexes in the Open Data Cube database and accessed when they are needed. Results from analyzations are being saved for further use. The system currently computes only mathematical equations such as NDVI=(NIR-RED)/(NIR+RED). 
Users interact with the `hellascube` CLI to submit analysis requests by area name or custom GeoJSON geometry.

---

## Architecture

```
hellascube CLI (Rust, user's Command Line Interface)
        │
        │  requests (JSON request)
        ▼
Rust Axum API ──────────────────► PostgreSQL(User data, API keys)
(Auth, caching, orchestration)
        │
        │  analysis job (JSON request)
        ▼
Python FastAPI
(Spectral analysis, Dask Threading, Computing Equations)
        │
        │  dc.load()(loading dataset)
        ▼
Open Data Cube
(Sentinel-2 L2A, Landsat 5/7/8/9)
        │
        │  compute
        ▼
Python FastAPI
        │
        │  results returned
        ▼
Rust Axum API ──────────────────► PostgreSQL
                                   (Results, request log, JSON)
        │
        └──────────────────────── response to user ──► hellascube CLI
```

---

## Components

### `CLI_HC` — Rust CLI (`hellascube`)

A terminal client built with [`clap`](https://github.com/clap-rs/clap). Communicates with the Axum API over HTTP using `reqwest`.

Features:
- Account creation and login (`hellascube login`, `hellascube create-account`)
- Index analysis commands: `hellascube ndvi`, `hellascube`, `hellascube ndci`, `hellascube ndti`, `hellascube ndmi`, `hellascube ndbi`, `hellascube ndsi`, `hellascube wofs`, `hellascube sdd`, `hellascube nbr`
- Area selection via `--area <city>` or `--default` (uses a registered GeoJSON)
- GeoJSON registration: `hellascube declare-geojson`
- Persistent config stored at `~/.hellascube/hc_config.toml`

### `API` — Rust Axum Server

The orchestration layer. Handles authentication, request routing, result caching, and forwarding analysis requests to the Python service.

- Authentication with Argon2 password hashing and SHA-256-hashed API keys
- API key expiry via `pg_cron`
- `SQLx` with runtime queries (no compile-time `DATABASE_URL` required)
- DB credentials loaded from `~/.hellascube/dbconfig.env`
- Axum `State`-based dependency injection for the connection pool

### `P_analyzations_HC` — Python FastAPI Service

The analysis backend. Interfaces directly with Open Data Cube and performs all spectral computation.

- ODC `dc.load()` with Dask chunking for performance
- SCL-based cloud and cloud-shadow masking
- Reflectance range filtering, NDI clamping to `[-1, 1]`
- NaN-aware statistics: mean, median, std, percentiles, coverage
- GeoJSON-based area search with multilingual name lookup across all `name`/`name:*` OSM tags
- Shared Dask `LocalCluster` managed via lifespan context
- GDAL environment variables tuned for S3 access (`AWS_REQUEST_PAYER=requester`)

---

## Supported Indices

| Index | Full Name                          | Satellite bands used         |
|-------|------------------------------------|------------------------------|
| NDVI  | Normalized Difference Vegetation Index | NIR, Red                 |
| NDWI  | Normalized Difference Water Index  | Green, NIR                   |
| NDCI  | Normalized Difference Chlorophyll Index | Red Edge, Red           |
| NDTI  | Normalized Difference Turbidity Index  | Red, Green              |
| NDMI  | Normalized Difference Moisture Index   | NIR, SWIR16             |
| NDBI  | Normalized Difference Built-up Index   | SWIR16, NIR             |
| NDSI  | Normalized Difference Snow Index       | Green, SWIR16           |
| NBR   | Normalized Burn Ratio                  | NIR, SWIR22             |
| WOfS | Water Observations from Space          | Multi-band               |
| SDD  | Secchi Disk Depth                      | Blue, Green, Red         |

---

## Database

A dedicated `hellas_cube` PostgreSQL database (separate from the ODC internal DB) stores:

- User accounts with UUID primary keys and a custom `email` domain type
- Computed analysis results as JSONB
- Request logs
- `created_at` / `updated_at` timestamps maintained by a trigger

---

## Configuration

| File | Purpose |
|------|---------|
| `~/.hellascube/hc_config.toml` | CLI config (API URL, auth token) |   (local to user for auth data such as e-mail, api key)
| `~/.hellascube/dbconfig.env`   | DB credentials for the Axum server | (will be removed)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| CLI | Rust, Clap, Reqwest, Serde, Toml |
| API Server | Rust, Axum, SQLx, Argon2, PostgreSQL |
| Analysis Service | Python, FastAPI, Open Data Cube, Xarray, Dask |
| Data | Sentinel-2 L2A, Landsat 8 (via AWS S3) |
| Database | PostgreSQL, pg_cron |

---

## Project Status

Active development as a Thesis project, International Hellenic University (IHU), Thessaloniki, Greece.

---
## Author

Christos Sapounas