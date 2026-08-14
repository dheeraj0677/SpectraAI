# Repository Baseline Report: SpectraAI

> **Repository URL:** [https://github.com/dheeraj0677/SpectraAI](https://github.com/dheeraj0677/SpectraAI)  
> **Audit Date:** August 14, 2026  
> **Auditor:** Antigravity Baseline Audit Agent  
> **Status:** Baseline Audit Completed (Read-Only)

---

## 1. Git Repository State & Commit History

### 1.1 Local Commit Identifiers
- **Current HEAD Commit SHA:** `3b12ab79f498233e94060c0320c62114b5f65a18`
- **Current Active Branch:** `improvement/phase1-stabilize`
- **Main Branch Commit SHA:** `0857ddc634566d4cf20078a55eee16dfb175ae20`
- **Remote `origin/main` Commit SHA:** `0857ddc634566d4cf20078a55eee16dfb175ae20`
- **Remote URL:** `https://github.com/dheeraj0677/SpectraAI.git` (fetch & push)

### 1.2 Local Commit Log
```
* 3b12ab7 (HEAD -> improvement/phase1-stabilize) fix: resolve install blocker, deprecations, and unit annotation bug
*   0857ddc (origin/main, origin/HEAD, main) Merge pull request #1 from dheeraj0677/feature/unilog-product-intelligence
|\  
| * a899de1 feat: add Unilog industrial taxonomy (UNSPSC/ETIM), CRI scorecard, SEO title generator, part interchange matching, and UniHack evaluation report
|/  
* 9ca221d feat: initial commit for SpectraAI - Multimodal Product Intelligence Engine
```

#### Detailed Commit Metadata
1. **Commit `3b12ab7`** (2026-08-14 16:54:57 +0530) — Viswa `<viswa@example.com>`
   - *Message:* `fix: resolve install blocker, deprecations, and unit annotation bug`
   - *Changes:* Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)` in `models.py` and `test_e2e.py`; migrated FastAPI startup from `@app.on_event` to `lifespan` in `main.py`; fixed `power_watts` unit annotation (`kW` -> `W`) in `extract.py`; updated `pyrightconfig.json` extraPaths; added `.python-version` (3.13), `CONTRIBUTING.md`, `backend/uploads/.gitkeep`.
2. **Commit `0857ddc`** (2026-08-13 23:18:52 +0530) — GOPI SETTY LAKSHMI DHEERAJ `<dheerajofficial06@gmail.com>`
   - *Message:* `Merge pull request #1 from dheeraj0677/feature/unilog-product-intelligence`
3. **Commit `a899de1`** (2026-08-13 23:18:26 +0530) — dheeraj0677 `<dheeraj0677@users.noreply.github.com>`
   - *Message:* `feat: add Unilog industrial taxonomy (UNSPSC/ETIM), CRI scorecard, SEO title generator, part interchange matching, and UniHack evaluation report`
4. **Commit `9ca221d`** (2026-08-05 22:46:18 +0530) — dheeraj0677 `<dheeraj0677@users.noreply.github.com>`
   - *Message:* `feat: initial commit for SpectraAI - Multimodal Product Intelligence Engine`

---

## 2. Tracked Files Inventory & Classification

Every tracked file in the repository is inventoried below and classified into one of seven standard categories:
- **Source:** Core application logic and user interface code.
- **Test:** Automated test suites, test runners, and test fixtures.
- **Documentation:** Markdown documentation, specifications, and architecture guides.
- **Config:** Package manifests, runtime configurations, build configurations, and IDE settings.
- **Data:** Seed datasets, category taxonomy catalogs, and sample data files.
- **Generated:** Machine-generated output reports, lockfiles, and test artifacts.
- **Vendor:** External dependencies (none tracked in git).

### 2.1 Complete File Inventory Table

| Relative Path | Classification | Size (Bytes) | Line Count | Purpose / Description |
|---|---|---|---|---|
| [.gitignore](file:///c:/Users/viswa/Desktop/SpectraAI/.gitignore) | Config | 299 | 22 | Git ignore rules (build artifacts, node_modules, .db, .env) |
| [.python-version](file:///c:/Users/viswa/Desktop/SpectraAI/.python-version) | Config | 5 | 1 | Python version declaration (`3.13`) |
| [BUILD_REPORT.md](file:///c:/Users/viswa/Desktop/SpectraAI/BUILD_REPORT.md) | Documentation | 8,394 | 126 | Initial build completion and verification report (v1.0) |
| [CONTRIBUTING.md](file:///c:/Users/viswa/Desktop/SpectraAI/CONTRIBUTING.md) | Documentation | 4,370 | 133 | Contribution guide, environment setup, and collaboration rules |
| [README.md](file:///c:/Users/viswa/Desktop/SpectraAI/README.md) | Documentation | 5,729 | 110 | Main project overview, quickstart instructions, and limitations |
| [UNIHACK_SPECTRAAI_REPORT.md](file:///c:/Users/viswa/Desktop/SpectraAI/UNIHACK_SPECTRAAI_REPORT.md) | Documentation | 17,320 | 231 | UniHack innovation challenge evaluation report (v1.1) |
| [backend/__init__.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/__init__.py) | Source | 37 | 3 | Backend package initialization |
| [backend/database.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/database.py) | Source | 5,841 | 136 | Async SQLite database access layer via `aiosqlite` |
| [backend/enrich.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/enrich.py) | Source | 7,369 | 178 | RAG enrichment, embedded retriever, UNSPSC & ETIM mapping |
| [backend/extract.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/extract.py) | Source | 13,223 | 305 | Multimodal extraction (Claude Vision VLM & deterministic fallback) |
| [backend/human_review.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/human_review.py) | Source | 3,993 | 117 | Human-in-the-loop review, field override, and audit logging |
| [backend/ingest.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/ingest.py) | Source | 1,313 | 39 | Source file ingestion and SHA-256 hash generation |
| [backend/knowledge_graph.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/knowledge_graph.py) | Source | 6,197 | 138 | NetworkX knowledge graph, sibling outlier checks, part interchange |
| [backend/main.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/main.py) | Source | 8,469 | 219 | FastAPI entrypoint, HTTP routes, SSE pipeline stream, lifespan |
| [backend/merge.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/merge.py) | Source | 2,766 | 73 | Multi-source concordance merge & conflict scoring (0.7x penalty) |
| [backend/models.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/models.py) | Source | 3,653 | 80 | Pydantic v2 domain models (`ProductRecord`, `FieldValue`, etc.) |
| [backend/pipeline.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/pipeline.py) | Source | 6,051 | 128 | 6-stage asynchronous intelligence pipeline orchestrator |
| [backend/requirements.txt](file:///c:/Users/viswa/Desktop/SpectraAI/backend/requirements.txt) | Config | 456 | 14 | Declared backend Python dependencies |
| [backend/seed_kb/category_taxonomies.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/category_taxonomies.json) | Data | 1,434 | 23 | Seed taxonomy definitions and standard category specifications |
| [backend/seed_kb/certification_definitions.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/certification_definitions.json) | Data | 827 | 18 | Seed industrial certification standards (CE, UL, IP65, RoHS) |
| [backend/seed_kb/typical_spec_ranges.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/typical_spec_ranges.json) | Data | 340 | 14 | Seed engineering specification bounds per category |
| [backend/seed_kb/unit_conventions.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/unit_conventions.json) | Data | 643 | 6 | Seed engineering unit aliases and standard conversion rules |
| [backend/uploads/.gitkeep](file:///c:/Users/viswa/Desktop/SpectraAI/backend/uploads/.gitkeep) | Config | 54 | 1 | Git placeholder keeping `backend/uploads/` directory tracked |
| [backend/validate.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/validate.py) | Source | 4,464 | 114 | Business rule validation & 0–100 Commerce Readiness Index (CRI) |
| [frontend/index.html](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/index.html) | Source | 965 | 18 | Frontend HTML entrypoint with font imports |
| [frontend/package.json](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/package.json) | Config | 489 | 23 | Frontend npm package manifest |
| [frontend/package-lock.json](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/package-lock.json) | Generated | 61,858 | 1,779 | Node dependency lockfile |
| [frontend/src/api.js](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/api.js) | Source | 2,519 | 74 | Frontend API client communicating with FastAPI backend |
| [frontend/src/App.css](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/App.css) | Source | 6,138 | 296 | Glassmorphism dark mode theme and component CSS |
| [frontend/src/App.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/App.jsx) | Source | 5,246 | 145 | Main React application layout (3-panel dashboard) |
| [frontend/src/components/ConsistencyPanel.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ConsistencyPanel.jsx) | Source | 1,464 | 31 | Catalog consistency and graph anomaly alert component |
| [frontend/src/components/FieldCard.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/FieldCard.jsx) | Source | 1,880 | 44 | Individual attribute card with confidence badge & modal trigger |
| [frontend/src/components/HumanReview.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/HumanReview.jsx) | Source | 9,626 | 226 | Bottom human-in-the-loop review bar, edit modal, and audit log |
| [frontend/src/components/KnowledgeGraph.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/KnowledgeGraph.jsx) | Source | 3,481 | 113 | D3.js force-directed knowledge graph visualization component |
| [frontend/src/components/PipelineStatus.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/PipelineStatus.jsx) | Source | 3,749 | 105 | Live SSE pipeline progress tracker with step indicators |
| [frontend/src/components/ProductRecord.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ProductRecord.jsx) | Source | 8,339 | 196 | Center panel product details display with JSON/CSV export |
| [frontend/src/components/ProvenancePopup.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/ProvenancePopup.jsx) | Source | 4,783 | 79 | Field provenance inspection modal with evidence snippets |
| [frontend/src/components/UploadPanel.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/components/UploadPanel.jsx) | Source | 4,929 | 137 | File upload dropzone & 1-click sample batch trigger component |
| [frontend/src/main.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/main.jsx) | Source | 243 | 10 | React root DOM mounter |
| [frontend/vite.config.js](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/vite.config.js) | Config | 323 | 16 | Vite build & dev-server proxy configuration |
| [pyrightconfig.json](file:///c:/Users/viswa/Desktop/SpectraAI/pyrightconfig.json) | Config | 39 | 5 | Pyright / Python language server configuration |
| [run_backend.bat](file:///c:/Users/viswa/Desktop/SpectraAI/run_backend.bat) | Config | 341 | 9 | Windows batch launcher for backend server |
| [run_frontend.bat](file:///c:/Users/viswa/Desktop/SpectraAI/run_frontend.bat) | Config | 210 | 9 | Windows batch launcher for frontend dev server |
| [test_data/sample_erp_export.csv](file:///c:/Users/viswa/Desktop/SpectraAI/test_data/sample_erp_export.csv) | Data | 232 | 2 | Sample sparse ERP CSV test fixture |
| [test_e2e.py](file:///c:/Users/viswa/Desktop/SpectraAI/test_e2e.py) | Test | 32,986 | 564 | 95-test end-to-end integration and verification suite |
| [test_report.json](file:///c:/Users/viswa/Desktop/SpectraAI/test_report.json) | Generated | 12,732 | 484 | JSON report generated by `test_e2e.py` |

---

## 3. Summary Metrics by Category

| Category | File Count | Total Lines | Total Size (Bytes) | % of Lines | % of Size |
|---|---|---|---|---|---|
| **Source** (Backend & Frontend) | 22 | 2,624 | 88,095 | 39.7% | 37.9% |
| **Test** (E2E Suite) | 1 | 564 | 32,986 | 8.5% | 14.2% |
| **Documentation** | 4 | 600 | 35,813 | 9.1% | 15.4% |
| **Config / Manifests / Scripts** | 9 | 100 | 2,216 | 1.5% | 1.0% |
| **Data** (Seed KB & Fixtures) | 5 | 63 | 3,476 | 1.0% | 1.5% |
| **Generated** (Lockfiles & Reports) | 2 | 2,263 | 74,590 | 34.3% | 32.1% |
| **Vendor** | 0 | 0 | 0 | 0.0% | 0.0% |
| **TOTALS** | **43** | **6,614** | **232,569** | **100.0%** | **100.0%** |

---

## 4. Repository Structure Map

```
SpectraAI/
├── .gitignore                           # Git ignore specifications
├── .python-version                      # Python version pinning (3.13)
├── pyrightconfig.json                   # Python LSP extraPaths config
├── README.md                            # Primary documentation & quickstart
├── CONTRIBUTING.md                      # Contribution guidelines & branch rules
├── BUILD_REPORT.md                      # Historical build report v1.0
├── UNIHACK_SPECTRAAI_REPORT.md          # Hackathon evaluation report v1.1
├── run_backend.bat                      # One-click backend startup script (Windows)
├── run_frontend.bat                     # One-click frontend startup script (Windows)
├── test_e2e.py                          # Comprehensive 95-test E2E verification harness
├── test_report.json                     # Latest E2E execution report artifact
├── test_data/
│   └── sample_erp_export.csv            # Sparse ERP CSV sample fixture
├── backend/
│   ├── __init__.py                      # Package marker
│   ├── main.py                          # FastAPI application & HTTP/SSE route handlers
│   ├── models.py                        # Pydantic v2 data models (ProductRecord, FieldValue)
│   ├── ingest.py                        # Source file upload & SHA-256 hash generator
│   ├── extract.py                       # Claude Sonnet VLM vision & fallback mock extractor
│   ├── merge.py                         # Multi-source concordance merge & conflict scoring
│   ├── enrich.py                        # RAG enrichment, embedded retriever, UNSPSC/ETIM
│   ├── knowledge_graph.py               # NetworkX graph, sibling comparisons, interchange
│   ├── validate.py                      # Rule validation engine & 0-100 CRI scorecard
│   ├── database.py                      # Asynchronous SQLite persistence layer (aiosqlite)
│   ├── pipeline.py                      # 6-stage async intelligence pipeline orchestrator
│   ├── human_review.py                  # Field-level override handler & audit logger
│   ├── requirements.txt                 # Backend Python package requirements
│   ├── uploads/
│   │   └── .gitkeep                     # Upload storage placeholder
│   └── seed_kb/                         # Embedded RAG Knowledge Base
│       ├── category_taxonomies.json     # Standard category schemas & accessories
│       ├── certification_definitions.json # Standard compliance definitions
│       ├── typical_spec_ranges.json     # Spec ranges for boundary validation
│       └── unit_conventions.json        # Engineering unit mappings & aliases
└── frontend/
    ├── index.html                       # HTML application template
    ├── package.json                     # Node.js dependencies & scripts
    ├── package-lock.json                # npm dependency lockfile
    ├── vite.config.js                   # Vite configuration & /api proxy
    └── src/
        ├── main.jsx                     # React entrypoint
        ├── App.jsx                      # Root 3-panel dashboard component
        ├── App.css                      # Glassmorphism dark-theme stylesheets
        ├── api.js                       # Frontend HTTP API client
        └── components/
            ├── UploadPanel.jsx          # File ingestion & sample load triggers
            ├── PipelineStatus.jsx       # Live SSE pipeline progress monitor
            ├── ProductRecord.jsx        # Structured attributes display & export
            ├── FieldCard.jsx            # Attribute card with confidence badges
            ├── KnowledgeGraph.jsx       # D3.js force-directed graph renderer
            ├── ConsistencyPanel.jsx     # Catalog outlier & anomaly flags
            ├── HumanReview.jsx          # Human-in-the-loop override & audit trail
            └── ProvenancePopup.jsx      # Source citation & evidence modal
```

---

## 5. Ignore Rules Analysis

The repository `.gitignore` defines rules for dependencies, build outputs, Python caches, database files, uploaded files, and environment files:

```gitignore
# Dependencies
node_modules/
frontend/node_modules/

# Build outputs
dist/
frontend/dist/

# Python cache & databases
__pycache__/
*.pyc
*.db
backend/product_intelligence.db
backend/uploads/*
!backend/uploads/.gitkeep

# Environment & IDE
.env
.env.local
.vscode/
.idea/
*.log
```

### 5.1 Ignore Rule Verification
- `backend/product_intelligence.db`: Dynamically generated SQLite database created upon backend startup or test runs; properly ignored.
- `backend/uploads/*` except `.gitkeep`: Uploaded test files during runtime are ignored while the directory structure remains tracked.
- `frontend/node_modules/` and `frontend/dist/`: Correctly excluded from tracking.
- `__pycache__/`: Ignored across all directories.
- Working tree status: Clean (`nothing to commit, working tree clean`).

---

## 6. Environment Baseline

- **Operating System:** Windows 11 (win32)
- **Shell:** PowerShell
- **Python Runtime:** Python `3.13.11`
- **Node.js Runtime:** Node.js `v24.13.0`
- **npm Version:** `11.6.2`
- **FastAPI Version:** `0.136.3`
- **Pydantic Version:** `2.13.4`
- **Vite Version:** `4.5.14`
- **React Version:** `18.2.0`
- **D3 Version:** `7.8.5`
