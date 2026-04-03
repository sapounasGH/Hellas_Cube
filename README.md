# Hellas Cube (Still in development)

> **Thesis Project** — A geospatial remote sensing platform for querying and analyzing satellite data over Greek regions.

Hellas Cube provides a full-stack toolchain for requesting, processing, and analyzing satellite imagery data. Given a geographic region and a date range, it retrieves datacubes and runs spectral indices such as **NDVI**, **NDCI**, and **WOFS** to support environmental and land-use analysis.

---

## Features

- **Datacube querying** — Request satellite data for any Greek city or region over a custom date range.
- **Spectral analysis** — Compute remote sensing indices including:
  - **NDVI** (Normalized Difference Vegetation Index) — measures vegetation health
  - **NDCI** (Normalized Difference Chlorophyll Index) — monitors water quality
  - **WOFS** (Water Observation from Space) — detects water coverage
- **REST API** — A Rust-powered backend for high-performance data serving.
- **CLI tool** — A command-line interface for scripting and automating datacube requests.
- **Python analysis layer** — Flexible Python scripts for post-processing and visualization of results.

---

## Author

**Christos Sapounas**

- GitHub: [@sapounasGH](https://github.com/sapounasGH)

---

## License

This project was developed as a university thesis. All rights reserved unless otherwise stated.
