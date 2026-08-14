# Improvement Backlog: SpectraAI

> **System Name:** SpectraAI Improvement Backlog  
> **Classification Scheme:** Confirmed Defects | Probable Risks | Documentation Inconsistencies | Missing Collaboration Infrastructure | Optional Product Enhancements  
> **Prioritization:** P0 (Blocker / Critical) | P1 (High) | P2 (Medium) | P3 (Low / Polish)

---

## 1. Confirmed Defects

### DEF-01: Deprecated `datetime.utcnow` in `SourceDocument` Model
- **Priority:** P1 (High)
- **Rationale:** While `ProductRecord` was updated to timezone-aware `datetime.now(timezone.utc)` in commit `3b12ab7`, `SourceDocument` in `backend/models.py` still defines `uploaded_at: datetime = Field(default_factory=datetime.utcnow)`. In Python 3.12+, `datetime.utcnow()` emits `DeprecationWarning` and produces naive datetime objects that risk timezone mismatch bugs when serialized or stored alongside timezone-aware timestamps.
- **Affected Files:**
  - [backend/models.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/models.py#L65-L71)
- **Acceptance Test:**
  - Instantiating `SourceDocument(source_id="test", source_type="pdf", file_path="test.pdf", filename="test.pdf")` produces a timezone-aware `datetime` with `uploaded_at.tzinfo == timezone.utc` without raising `DeprecationWarning`.

---

### DEF-02: Hardcoded Absolute Path in `run_backend.bat`
- **Priority:** P1 (High)
- **Rationale:** `run_backend.bat` contains a hardcoded author-specific path: `"C:\Users\Dheer\AppData\Local\Programs\Python\Python312\python.exe"`. Running this script on any other developer machine or operating environment causes a fatal script error (`The system cannot find the path specified`).
- **Affected Files:**
  - [run_backend.bat](file:///c:/Users/viswa/Desktop/SpectraAI/run_backend.bat#L7-L8)
- **Acceptance Test:**
  - Executing `run_backend.bat` in a standard Windows environment uses the system `python` executable on PATH (or active virtual environment) and successfully starts the Uvicorn server without hardcoded user directories.

---

### DEF-03: Typo in Seed KB Category Taxonomy ("Monting Flange Kit")
- **Priority:** P2 (Medium)
- **Rationale:** In `backend/seed_kb/category_taxonomies.json` line 7, the accessory list contains the misspelled item `"Monting Flange Kit"` instead of `"Mounting Flange Kit"`. This typo directly propagates through the RAG enrichment pipeline into enriched product records and client-facing exports.
- **Affected Files:**
  - [backend/seed_kb/category_taxonomies.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/category_taxonomies.json#L7)
  - [test_e2e.py](file:///c:/Users/viswa/Desktop/SpectraAI/test_e2e.py#L311)
- **Acceptance Test:**
  - Running RAG enrichment for *Industrial Motors & Drives* produces `accessories` containing `"Mounting Flange Kit"` with correct spelling, and all integration tests pass.

---

### DEF-04: Pytest Discovery Teardown Failure (`ValueError: I/O operation on closed file`)
- **Priority:** P2 (Medium)
- **Rationale:** Running `pytest` fails with `ValueError: I/O operation on closed file` because `test_e2e.py` overrides `sys.stdout = io.TextIOWrapper(...)` for Windows console UTF-8 output at import time. This collides with pytest's global output capturing fixture (`_pytest.capture`). Furthermore, tests are defined inside an async `main()` runner rather than standard discoverable `def test_*()` functions.
- **Affected Files:**
  - [test_e2e.py](file:///c:/Users/viswa/Desktop/SpectraAI/test_e2e.py#L17)
- **Acceptance Test:**
  - Running `pytest` from the repository root discovers and executes tests cleanly without `sys.stdout` stream collisions or teardown exceptions.

---

### DEF-05: Empty `onEditField` Callback Handler in `App.jsx`
- **Priority:** P2 (Medium)
- **Rationale:** In `frontend/src/App.jsx` line 118, `<ProductRecord record={selectedProduct} onEditField={(field, val) => {}} />` passes a no-op dummy callback. If child components invoke `onEditField`, no state update or modal trigger occurs in the parent container.
- **Affected Files:**
  - [frontend/src/App.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/App.jsx#L118)
  - [frontend/src/components/ProductRecord.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ProductRecord.jsx#L6)
- **Acceptance Test:**
  - Clicking an edit trigger within `ProductRecord` either directly launches the human override workflow or cleanly passes the edit request to the root state handler.

---

### DEF-06: Hardcoded UltraDrive Fallback Defaults in `pipeline.py`
- **Priority:** P2 (Medium)
- **Rationale:** In `backend/pipeline.py` lines 99-108, the construct `merged_fields.pop("product_name", FieldValue(value="UltraDrive X500 Inverter Motor", ...))` injects UltraDrive strings if the field is missing from extractions. If a user uploads an arbitrary non-UltraDrive product and extraction returns empty fields, the pipeline silently assigns UltraDrive strings rather than maintaining `FieldValue(status="missing")`.
- **Affected Files:**
  - [backend/pipeline.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/pipeline.py#L99-L108)
- **Acceptance Test:**
  - Running the pipeline on an empty extraction returns empty/missing fields with `status="missing"` instead of defaulting to UltraDrive product name and model.

---

## 2. Probable Risks

### RSK-01: In-Memory Graph and Job Trackers Lost in Multi-Worker Environments
- **Priority:** P1 (High)
- **Rationale:** `job_trackers` in `backend/pipeline.py` and graph `G` in `backend/knowledge_graph.py` are stored in global Python process memory. If FastAPI is deployed with multiple Uvicorn workers (`uvicorn --workers 4`), state will not be shared across processes, resulting in 404 errors on SSE progress polling and inconsistent graph views.
- **Affected Files:**
  - [backend/pipeline.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/pipeline.py#L43)
  - [backend/knowledge_graph.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/knowledge_graph.py#L6)
- **Acceptance Test:**
  - Graph nodes and pipeline job statuses are backed by SQLite or shared state cache (or single-worker constraint is strictly documented and enforced in production deployment scripts).

---

### RSK-02: Model Identifier Incompatibility in Anthropic API Call (`claude-sonnet-4-6`)
- **Priority:** P1 (High)
- **Rationale:** In `backend/extract.py` lines 75 and 122, the model identifier is set to `claude-sonnet-4-6`. Standard Anthropic model strings are `claude-3-5-sonnet-20241022`, `claude-3-7-sonnet-20250219`, or alias `claude-3-5-sonnet-latest`. If a valid `ANTHROPIC_API_KEY` is supplied, the API call will return a 404 model not found error and fall back silently to mock mode.
- **Affected Files:**
  - [backend/extract.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/extract.py#L75)
  - [backend/extract.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/extract.py#L122)
- **Acceptance Test:**
  - With a valid `ANTHROPIC_API_KEY`, live Claude Vision extraction completes against the supported model alias (e.g. `claude-3-5-sonnet-latest`) without returning 404 or falling back.

---

### RSK-03: Unsanitized File Paths During Ingestion
- **Priority:** P2 (Medium)
- **Rationale:** In `backend/ingest.py` line 37, `dest_path = UPLOAD_DIR / filename` writes uploaded files directly using the client-supplied filename without sanitization (e.g. `Path(filename).name`), leaving the backend exposed to path traversal or overwriting existing files with identical names.
- **Affected Files:**
  - [backend/ingest.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/ingest.py#L36-L40)
- **Acceptance Test:**
  - File upload handles filenames with path components (e.g., `../../malicious.pdf` or duplicate names) safely by stripping directory paths and appending unique hashes.

---

### RSK-04: SSE Connection Queue Leak on Client Disconnect
- **Priority:** P2 (Medium)
- **Rationale:** In `backend/main.py:pipeline_status_sse`, listeners are appended to `tracker.listeners`. If the client disconnects or closes the browser tab before the pipeline reaches `complete`, the queue listener is never removed from `tracker.listeners`.
- **Affected Files:**
  - [backend/main.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/main.py#L121-L156)
  - [backend/pipeline.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/pipeline.py#L23-L41)
- **Acceptance Test:**
  - When SSE client aborts connection, a `finally` block unregisters the listener from `tracker.listeners`.

---

### RSK-05: Synchronous Graph Export Blocking Event Loop
- **Priority:** P3 (Low)
- **Rationale:** In `backend/main.py` line 213, `GET /api/graph` is defined as a synchronous `def get_knowledge_graph()`. While fast for small graphs, as the catalog grows to thousands of nodes, serializing the graph in the main thread will block the FastAPI async event loop.
- **Affected Files:**
  - [backend/main.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/main.py#L212-L215)
- **Acceptance Test:**
  - Graph serialization runs asynchronously or in an async thread pool (`asyncio.to_thread`) without blocking request handling.

---

## 3. Documentation Inconsistencies

### DOC-01: Discrepancy in Historical Test Count (90 vs 95 Tests)
- **Priority:** P2 (Medium)
- **Rationale:** `BUILD_REPORT.md` states "90 / 90 E2E Tests Passed" (dated August 6, 2026), whereas `UNIHACK_SPECTRAAI_REPORT.md` and `test_e2e.py` / `test_report.json` reflect the updated 95-test suite (dated August 13/14, 2026).
- **Affected Files:**
  - [BUILD_REPORT.md](file:///c:/Users/viswa/Desktop/SpectraAI/BUILD_REPORT.md#L4)
  - [UNIHACK_SPECTRAAI_REPORT.md](file:///c:/Users/viswa/Desktop/SpectraAI/UNIHACK_SPECTRAAI_REPORT.md#L6)
- **Acceptance Test:**
  - `BUILD_REPORT.md` is updated or annotated to clarify that v1.0 had 90 tests and v1.1+ expanded the suite to 95 tests.

---

### DOC-02: Pipeline Status UI Label Refers to Removed `Chroma`
- **Priority:** P3 (Low)
- **Rationale:** In `frontend/src/components/PipelineStatus.jsx` line 8, STAGES[3] is labeled `'4. Chroma RAG Enrichment'`, but `chromadb` was removed from dependencies and replaced with the lightweight in-memory `EmbeddedRetriever`.
- **Affected Files:**
  - [frontend/src/components/PipelineStatus.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/PipelineStatus.jsx#L8)
- **Acceptance Test:**
  - Stage label in `PipelineStatus.jsx` is updated to `'4. Seed RAG KB Enrichment'` to reflect the current implementation.

---

## 4. Missing Collaboration Infrastructure

### INF-01: Missing Automated CI/CD GitHub Actions Workflow
- **Priority:** P1 (High)
- **Rationale:** There is currently no `.github/workflows/ci.yml` in the repository. Pull requests cannot automatically verify that `python test_e2e.py` passes and `npm run build` succeeds across different operating systems.
- **Affected Files:**
  - New file: `.github/workflows/ci.yml`
- **Acceptance Test:**
  - GitHub Actions workflow executes on push and pull_request, running linting, `python test_e2e.py`, and `npm --prefix frontend run build`.

---

### INF-02: Missing PR and Issue Templates
- **Priority:** P2 (Medium)
- **Rationale:** To enforce the collaboration rules specified in `CONTRIBUTING.md` (e.g. testing mode declaration, branch naming, human review requirement), standardized pull request and issue templates are needed.
- **Affected Files:**
  - New file: `.github/PULL_REQUEST_TEMPLATE.md`
  - New files in: `.github/ISSUE_TEMPLATE/`
- **Acceptance Test:**
  - Opening a PR or issue on GitHub renders structured checklists for testing mode, verification evidence, and review approval.

---

### INF-03: Missing Pre-Commit / Code Formatting Configs
- **Priority:** P3 (Low)
- **Rationale:** No linting / formatting config (e.g., `ruff`, `eslint`, `prettier`) is tracked, making style enforcement manual across contributors.
- **Affected Files:**
  - `pyproject.toml` or `ruff.toml`
  - `frontend/.eslintrc.json`
- **Acceptance Test:**
  - `ruff check` and `npm run lint` execute cleanly with zero configuration errors.

---

## 5. Optional Product Enhancements

### ENH-01: True Offline PDF Table Extraction with `pypdf`
- **Priority:** P2 (Medium)
- **Rationale:** `pypdf` is installed, but `backend/extract.py` currently uses static fallback dictionaries when offline. Implementing basic rule-based text/table parsing using `pypdf` when API key is missing would provide real extraction on arbitrary PDF files without needing cloud LLM tokens.
- **Affected Files:**
  - [backend/extract.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/extract.py#L217-L274)
- **Acceptance Test:**
  - Uploading an arbitrary offline PDF datasheet extracts text chunks and key-value specs using `pypdf` without calling external APIs.

---

### ENH-02: Multi-Product Catalog Batch Dashboard
- **Priority:** P2 (Medium)
- **Rationale:** The current frontend is primarily optimized for inspecting one product at a time. A multi-product batch view showing a grid of all catalog products with their CRI scores, conflict badges, and batch approval actions would improve enterprise efficiency.
- **Affected Files:**
  - [frontend/src/App.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/App.jsx)
  - [frontend/src/components/ProductRecord.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ProductRecord.jsx)
- **Acceptance Test:**
  - User can view a catalog table listing all products, filter by CRI score or conflict status, and trigger batch approvals.

---

### ENH-03: Export to Unilog C1 PIM XML / JSON Schema
- **Priority:** P3 (Low)
- **Rationale:** Expanding export capabilities from generic JSON/CSV to direct Unilog C1 PIM syndication format will enable instant integration with enterprise distributor catalogs.
- **Affected Files:**
  - [backend/models.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/models.py)
  - [frontend/src/components/ProductRecord.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ProductRecord.jsx)
- **Acceptance Test:**
  - Export dropdown includes "Unilog C1 Schema", producing valid PIM syndication XML/JSON.
