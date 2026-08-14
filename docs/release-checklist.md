# SpectraAI v1.0.0 Release Verification Checklist

This release readiness checklist must be completed prior to tagging and publishing a production release of SpectraAI.

---

## 1. Versioning & Package Manifests
- [x] Backend version set in [`backend/config.py`](file:///c:/Users/viswa/Desktop/SpectraAI/backend/config.py) (`app_version = "1.0.0"`).
- [x] Frontend version set in [`frontend/package.json`](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/package.json) (`"version": "1.0.0"`).
- [x] Root `.python-version` pinned to `3.13`.
- [x] Root `.nvmrc` and `.node-version` pinned to Node `20` / `24`.

---

## 2. Changelog & Governance
- [x] [`CHANGELOG.md`](file:///c:/Users/viswa/Desktop/SpectraAI/CHANGELOG.md) updated following Keep a Changelog format.
- [x] [`LICENSE`](file:///c:/Users/viswa/Desktop/SpectraAI/LICENSE) MIT copyright active.
- [x] [`ATTRIBUTION.md`](file:///c:/Users/viswa/Desktop/SpectraAI/ATTRIBUTION.md) lists all third-party dependencies and synthetic fixtures.
- [x] [`SECURITY.md`](file:///c:/Users/viswa/Desktop/SpectraAI/SECURITY.md) and [`CODE_OF_CONDUCT.md`](file:///c:/Users/viswa/Desktop/SpectraAI/CODE_OF_CONDUCT.md) active.
- [x] [`.github/CODEOWNERS`](file:///c:/Users/viswa/Desktop/SpectraAI/.github/CODEOWNERS) assigns confirmed maintainer `@dheeraj0677`.

---

## 3. Dependency & Security Audit
- [x] Bounded dependencies in `backend/requirements.txt` with zero unpinned wildcards.
- [x] Zero hardcoded secrets, passwords, or live API keys committed in git history.
- [x] `.env.example` contains variable names only with safe placeholder text.
- [x] No `datetime.utcnow()` deprecation warnings; all timestamps are timezone-aware `datetime.now(timezone.utc)`.

---

## 4. Test Verification & Continuous Integration
- [x] Pytest suite passes: `pytest -v` (**60/60 tests passed**).
- [x] Compatibility runner passes: `python test_e2e.py` (**131/131 tests passed**).
- [x] Frontend smoke tests pass: `npm --prefix frontend test` (**21/21 tests passed**).
- [x] Frontend production bundle built cleanly: `npm --prefix frontend run build` (Exit code 0).
- [x] GitHub Actions CI workflow [`.github/workflows/ci.yml`](file:///c:/Users/viswa/Desktop/SpectraAI/.github/workflows/ci.yml) validated.

---

## 5. Performance & Telemetry Profiling
- [x] Deterministic benchmark executed via `python benchmark_pipeline.py`.
- [x] Performance report generated at [`docs/performance-benchmark.md`](file:///c:/Users/viswa/Desktop/SpectraAI/docs/performance-benchmark.md).
- [x] Database indexes created on `products(review_status)` and `human_edits(product_id)`.
- [x] Live diagnostics endpoint [`GET /api/diagnostics`](file:///c:/Users/viswa/Desktop/SpectraAI/docs/api-contract.md) reporting stage timings.

---

## 6. Rollback & Emergency Protocol
- If a regression is discovered after deployment:
  1. Roll back deployment to git commit `3b12ab7` (or previous stable tag).
  2. Restore SQLite database snapshot from backup or reset state with `Remove-Item backend/product_intelligence.db`.
  3. Rebuild frontend bundle with `npm --prefix frontend run build`.
