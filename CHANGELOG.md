# Changelog

All notable changes to SpectraAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-14

### Added
- **Unit Normalization Engine (`backend/normalize.py`):** Non-destructive, transparent unit standardizer for Power (`kW`/`HP` → `W`), Voltage (`kV`/`mV`/`VAC` → `V`), Weight (`lbs`/`g` → `kg`), Temperature (`°F` → `°C`), and Dimensions (`in` → `mm`).
- **Structured Observability & Telemetry (`backend/telemetry.py`):** Correlation ID middleware (`X-Correlation-ID`, `X-Response-Time-Ms`) and `GET /api/diagnostics` endpoint tracking high-resolution stage latencies and review queues.
- **Commerce Readiness Index (CRI) 5-Dimension Scorecard:** UI and backend breakdown across Identity, Specs Depth, Taxonomy, Commerce Content, and Quality.
- **Industrial Taxonomy Mapping:** UNSPSC Commodity Codes and ETIM Technical Classes automatically enriched via seed RAG knowledge base.
- **Deterministic Pipeline Benchmark (`benchmark_pipeline.py`):** Reproducible performance profiler generating `docs/performance-benchmark.md`.
- **Modular Pytest Suite (`tests/`):** 60 modular unit, integration, API, and e2e tests with isolated SQLite database fixtures.
- **Frontend Smoke Suite (`frontend/test_smoke.js`):** 21 automated React logic and CSV export smoke tests.
- **GitHub Actions CI (`.github/workflows/ci.yml`):** Automated PR pipeline running linting, backend tests, frontend builds, and offline health checks with artifact uploading.
- **Community Governance & Legal Infrastructure:** `LICENSE` (MIT), `ATTRIBUTION.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `.github/CODEOWNERS`, and structured issue templates.

### Changed
- **FastAPI Hardening:** Typed response models, centralized settings (`backend/config.py`), upload payload sanitization, 50MB upload limits, and 404/422 structured `ErrorResponse`.
- **Offline PDF Parsing:** Added direct `pypdf` extraction to parse real technical PDFs offline without requiring Anthropic API keys in baseline execution.
- **Human-in-the-Loop Review:** Immutable provenance appending on human edits with observation type `human_verified` and audit trail history modal.
- **Database Optimization:** Added SQLite indexes on `products(review_status)` and `human_edits(product_id)`.

### Fixed
- Replaced deprecated `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` across all models and test runners.
- Corrected power unit annotation bug (`kW` → `W`).
- Fixed top-level stdout capture collision in `test_e2e.py` during Pytest test discovery.
