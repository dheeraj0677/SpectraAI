# Current Architecture Specification: SpectraAI

> **System Name:** SpectraAI — Multimodal Industrial Product Intelligence Engine  
> **Status:** Current Architecture as of Commit `3b12ab7`  
> **Language / Frameworks:** Python 3.12+ (FastAPI, Pydantic v2, NetworkX, aiosqlite) + React 18 (Vite, D3.js)

---

## 1. System Overview & Architecture Diagram

SpectraAI ingests heterogeneous, unstandardized manufacturer product data across multiple modalities (PDF technical datasheets, nameplate photographs, and sparse ERP CSV exports). It resolves cross-source data conflicts, enriches missing fields against an embedded seed knowledge base, standardizes taxonomy against UNSPSC and ETIM industrial classifications, checks catalog consistency using a graph anomaly engine, and outputs commerce-ready, source-cited product intelligence records backed by an immutable human-in-the-loop audit trail.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 1. MULTIMODAL INGESTION                                     │
│  [PDF Datasheets]          [Nameplate Images]          [ERP CSV Exports]                   │
│         │                          │                          │                             │
│         └──────────────────────────┼──────────────────────────┘                             │
│                                    v                                                        │
│                    backend/ingest.py: SHA-256 Hashing                                       │
│                    backend/database.py: Save SourceDocument                                 │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            2. MULTIMODAL EXTRACTION                                         │
│  backend/extract.py                                                                         │
│  ├── Live Mode: Claude 3.5 Sonnet Vision (output_config JSON Schema)                        │
│  └── Fallback Mode: Deterministic synthetic extraction for offline demo / CI testing        │
│  Every extracted field includes: Value, Unit, Confidence (0.0-1.0), Location, Raw Snippet   │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       3. MULTI-SOURCE MERGE & CONFLICT RESOLUTION                           │
│  backend/merge.py                                                                           │
│  ├── Concordance: Sources agree -> Boost confidence (min(1.0, max(conf) + 0.08))            │
│  └── Disagreement: Sources disagree -> Status 'conflicted', 0.7x penalty, candidate array   │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                      4. RAG KNOWLEDGE BASE ENRICHMENT & TAXONOMY                            │
│  backend/enrich.py + backend/seed_kb/*.json                                                 │
│  ├── EmbeddedRetriever: Fills standard accessories & certifications from category schemas   │
│  ├── Default Warranty: 24 Months Standard Warranty (seed standards grounded)               │
│  ├── UNSPSC v24.0 Commodity Mapping (e.g. 26101100 - Electric Motors)                       │
│  ├── ETIM 9.0 International Classification (e.g. EC001851 Electric Motor)                  │
│  └── SEO Title Synthesis Engine: [Manufacturer] [Name] [Voltage] [Power] Model [Model#]     │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    5. KNOWLEDGE GRAPH & ANOMALY DETECTION ENGINE                            │
│  backend/knowledge_graph.py                                                                 │
│  ├── NetworkX DiGraph: Nodes (products, categories, accessories), Edges (belongs_to, etc.)  │
│  ├── Sibling Outlier Anomaly Check: Flags weight/specs deviating >2.5x from category mean   │
│  └── Industrial Part Interchange: Recommends substitute products with match confidence      │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    6. VALIDATION & COMMERCE READINESS (CRI)                                 │
│  backend/validate.py                                                                        │
│  ├── Business Rules: Voltage sanity (12V-100kV), weight/power numeric range validation      │
│  ├── Overall Confidence: Weighted mean of all populated field confidence scores             │
│  └── Commerce Readiness Index (CRI 0-100%): Identity, Specs, Taxonomy, Content, Quality     │
└────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                     │
                                     v
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    7. SQLITE PERSISTENCE & HUMAN AUDIT TRAIL                                │
│  backend/database.py + backend/human_review.py                                              │
│  ├── Tables: `sources`, `products`, `human_edits`                                           │
│  ├── Human Overrides: Field corrections update value, confidence -> 1.0, provenance trail   │
│  └── Approval: Record marked approved, audit trail recorded with reviewer & timestamp       │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Architecture & Component Inspection

### 2.1 Backend Entrypoint & Lifecycle ([backend/main.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/main.py))
- **Framework:** FastAPI with Uvicorn ASGI server.
- **Application Lifespan:** Managed using modern `asynccontextmanager` (`@asynccontextmanager async def lifespan(app: FastAPI)`):
  1. Initializes SQLite database tables via `database.init_db()`.
  2. Checks if the product catalog is empty. If empty, automatically executes `pipeline.run_product_intelligence_pipeline()` with seed demo sources (`pdf_demo`, `image_demo`, `csv_demo`) to ensure instant out-of-the-box readiness (`PROD-DEMO-X500`).
- **CORS Configuration:** Permissive CORS enabled (`allow_origins=["*"]`) to support Vite local development on port `5173`.
- **API Endpoints:**
  - `GET /`: Health check and documentation links.
  - `POST /api/upload`: Multi-file multipart upload (`UploadFile`) for PDF, image, and CSV sources.
  - `POST /api/demo/load-sample`: 1-click synthetic batch trigger returning a tracking `job_id`.
  - `POST /api/pipeline/run`: Triggers the 6-stage asynchronous intelligence pipeline for given `source_ids`.
  - `GET /api/pipeline/status/{job_id}`: Server-Sent Events (SSE) stream broadcasting real-time pipeline stage progress (0-100%) and status messages.
  - `GET /api/products`: Lists all stored product intelligence summaries.
  - `GET /api/products/{product_id}`: Retrieves full `ProductRecord` including specifications, provenance receipts, and graph consistency warnings.
  - `PUT /api/products/{product_id}/fields/{field_name}`: Human-in-the-loop field correction and audit logging.
  - `POST /api/products/{product_id}/approve`: Approves a product record.
  - `GET /api/products/{product_id}/history`: Returns immutable field correction audit history.
  - `GET /api/graph`: Exports NetworkX graph in D3-compatible `{nodes, links}` JSON format.

### 2.2 Data Models ([backend/models.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/models.py))
All models are built using **Pydantic v2**:
- `Provenance`: Non-repudiable receipt tracking `source_id`, `source_type` (`pdf`, `image`, `csv`, `rag_enrichment`, `kg_inference`, `human_correction`), `location` (e.g. `Page 1, Header`), `extraction_method`, `confidence` (float 0.0-1.0), and `raw_snippet`.
- `FieldValue`: Container for an attribute value (string/number/bool/null), `unit`, `confidence`, `provenance` list, `status` (`extracted`, `enriched`, `conflicted`, `human_verified`, `missing`, `needs_review`), and `conflict_candidates` list.
- `ProductRecord`: Complete structured entity containing identity fields (`product_name`, `manufacturer`, `model_number`, `sku`, `category`), commerce fields (`description_short`, `description_long`, `key_features`, `unspsc_code`, `etim_class`, `commerce_readiness_score`, `cri_breakdown`, `seo_title`, `interchangeable_parts`), open-ended `specifications` dict (`Dict[str, FieldValue]`), compliance fields (`certifications`, `warranty`, `country_of_origin`), graph relationships (`compatible_with`, `replaces`, `accessories`), and metadata (`overall_confidence`, `review_status`, `human_edits_log`, timestamps).
- `SourceDocument`: Metadata for uploaded raw source files with cryptographic SHA-256 ID.
- `PipelineRunRequest` & `HumanEditRequest`: Request payloads for pipeline triggers and human review overrides.

### 2.3 Ingestion Module ([backend/ingest.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/ingest.py))
- File type detection based on extension: `.pdf` -> `pdf`; `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff` -> `image`; `.csv` -> `csv`.
- Cryptographic source registration: Calculates SHA-256 checksum of raw file bytes, taking the first 12 hex characters to generate deterministic IDs (e.g., `pdf_a1b2c3d4e5f6`).
- Upload persistence: Writes incoming files to `backend/uploads/`.

### 2.4 Multimodal Extraction Module ([backend/extract.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/extract.py))
- Supports dual execution modes:
  1. **Live Claude Vision Mode:** When `ANTHROPIC_API_KEY` is present, converts PDF/images to Base64 and issues structured extraction requests to Claude Sonnet (`model="claude-sonnet-4-6"`) with a strict JSON schema enforcing `{fields: [{field_name, value, unit, confidence, location, raw_snippet}]}`.
  2. **Deterministic Fallback / Mock Mode:** When API key is absent (e.g. local offline demo or test runner), provides pre-seeded synthetic extractions for the UltraDrive X500 motor across PDF, image, and CSV sources. Intentionally injects a voltage discrepancy (`480V` in PDF vs `460V` in image) to demonstrate conflict resolution.
- CSV extraction (`extract_from_csv`): Parses CSV rows using `csv.DictReader`, mapping column headers to snake_case field names with 0.95 confidence and exact row/column provenance.

### 2.5 Multi-Source Merge & Conflict Engine ([backend/merge.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/merge.py))
- Combines candidate `FieldValue` objects across all ingested sources per attribute name:
  - **Concordance (Agreement):** When all sources agree on a normalized value, merges provenance traces, picks the highest individual confidence, and applies a confidence boost (`min(1.0, max(conf) + 0.08)`), setting status to `extracted`.
  - **Disagreement (Conflict):** When sources report distinct values (e.g. `480V` vs `460V`), flags status as `conflicted`, retains all candidate values in `conflict_candidates`, combines provenance traces, and applies a **0.7x penalty** to the highest confidence candidate.

### 2.6 RAG Enrichment & Industrial Taxonomy Engine ([backend/enrich.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/enrich.py))
- **EmbeddedRetriever:** Curated in-memory retriever that reads seed JSON files from `backend/seed_kb/` without external vector database overhead.
- **Taxonomy Enrichment:**
  - Auto-assigns common accessories (e.g., *Braking Resistor Module*, *Mounting Flange Kit*) and typical certifications from category taxonomies if omitted in raw sources.
  - Supplies default manufacturer warranty (*24 Months Standard Warranty*) with `rag_enrichment` provenance.
  - **UNSPSC Mapping:** Standardizes product category to UNSPSC codes (e.g. `26101100 - Electric Motors`, `40141600 - Valves`).
  - **ETIM Mapping:** Standardizes product category to ETIM 9.0 classes (e.g. `EC001851 (Electric Motor)`).
  - **SEO Copy Generator:** Generates structured e-commerce titles formatted as `[Manufacturer] [Product Name] [Voltage] [Power] Model [Model Number]`.

### 2.7 Knowledge Graph & Anomaly Detection Engine ([backend/knowledge_graph.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/knowledge_graph.py))
- Built on **NetworkX** (`nx.DiGraph`):
  - Pre-seeded with category nodes (`Industrial Motors & Drives`), reference sibling products (`Ref-Drive X400`, `Ref-Drive X450`), and accessory nodes.
  - Dynamically links ingested products to categories (`belongs_to`), accessories (`has_accessory`), compatible products (`compatible_with`), and superseded models (`replaces`).
- **Catalog Anomaly & Outlier Detection:** Identifies category sibling products and calculates average specifications (e.g. category average weight = 46.4 kg). If an ingested product's specification deviates by >2.5x or <0.3x (e.g. weight = 5,000 kg), generates an outlier warning for the reviewer.
- **Part Interchange Recommender:** Matches sibling products with identical voltage and category, producing interchange recommendations with match confidence scores (e.g. 95.0%).
- **Graph Export:** Converts NetworkX nodes and edges into D3 force-directed JSON format `{nodes, links}`.

### 2.8 Business Rules Validation & CRI Scorecard ([backend/validate.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/validate.py))
- **Engineering Sanity Checks:** Validates electrical voltage (12V–100,000V), physical weight (0.01kg–50,000kg), and power (1W–1,000,000W) using regex-based numeric extractors. Invalid specifications are penalized (confidence halved) and marked `needs_review`.
- **Overall Confidence Calculation:** Computes the arithmetic mean of all non-empty core and specification field confidence scores.
- **Review Status Assignment:** Automatically transitions record to `needs_review` if `overall_confidence < 0.75` or if any field remains `conflicted`; otherwise sets to `pending`.
- **Commerce Readiness Index (CRI 0–100%):** Weighted scorecard evaluating:
  1. *Identity Completeness (25 pts):* Name (8), Manufacturer (8), Model Number (9).
  2. *Specification Depth (25 pts):* Coverage of technical specifications.
  3. *Taxonomy Compliance (20 pts):* Category (8), UNSPSC (6), ETIM (6).
  4. *Commerce Content (15 pts):* Short description (5), Long description (5), SEO title (5).
  5. *Quality & Accuracy (15 pts):* Baseline 15 pts with deductions for conflicts (-8) or low confidence (-5).

### 2.9 SQLite Persistence Layer ([backend/database.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/database.py))
- Uses **aiosqlite** for non-blocking asynchronous database operations against `backend/product_intelligence.db`.
- **Schema:**
  - `sources`: `(source_id TEXT PRIMARY KEY, source_type TEXT, file_path TEXT, filename TEXT, uploaded_at TEXT)`
  - `products`: `(product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT, overall_confidence REAL, review_status TEXT, record_json TEXT, created_at TEXT, updated_at TEXT)`
  - `human_edits`: `(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT, field_name TEXT, old_value TEXT, new_value TEXT, reviewer TEXT, timestamp TEXT, reason TEXT)`

### 2.10 Pipeline Orchestrator ([backend/pipeline.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/pipeline.py))
- Coordinates the 6 stages in sequence:
  1. *Ingestion (10-15%):* Source document retrieval and validation.
  2. *Extraction (30-45%):* Multimodal VLM and CSV parsing.
  3. *Merging (60%):* Field concordance and conflict scoring.
  4. *Enrichment (75%):* Seed RAG enrichment, UNSPSC/ETIM mapping, and SEO title synthesis.
  5. *Knowledge Graph (85%):* Graph expansion, sibling outlier checks, part interchange.
  6. *Validation (95-100%):* Business rule execution, CRI calculation, and SQLite persistence.
- Manages `PipelineProgressTracker` instances emitting real-time event updates to SSE listeners.

### 2.11 Human Review & Audit Module ([backend/human_review.py](file:///c:/Users/viswa/Desktop/SpectraAI/backend/human_review.py))
- `log_human_edit`: Updates core or specification field value, appends a `human_correction` provenance entry (confidence = 1.0, status = `human_verified`), appends to in-memory `human_edits_log`, persists to the SQLite `human_edits` table, re-executes validation, and saves the updated product record.
- `approve_record`: Sets `review_status = "approved"`, logs an approval event in the audit trail, and persists to the database.

---

## 3. Seed Knowledge Base Files ([backend/seed_kb/](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/))

1. [category_taxonomies.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/category_taxonomies.json): Defines schemas, standard specs, typical certifications, and common accessories for:
   - *Industrial Motors & Drives*
   - *Industrial Controllers & PLCs*
   - *Flow Control & Valves*
2. [certification_definitions.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/certification_definitions.json): Explanations of CE Mark, UL 508C, IP65, and RoHS.
3. [typical_spec_ranges.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/typical_spec_ranges.json): Engineering numerical boundaries for voltage, weight, and power across industrial categories.
4. [unit_conventions.json](file:///c:/Users/viswa/Desktop/SpectraAI/backend/seed_kb/unit_conventions.json): Standard units (`V`, `W`, `kg`, `°C`), aliases, and conversion rules.

---

## 4. Frontend Architecture & Visual Components

### 4.1 Frontend Framework & Build
- Built with **React 18** and **Vite 4**.
- Styling uses pure **Vanilla CSS** (`App.css`) with CSS custom properties, glassmorphism backdrop blur filters (`rgba(18, 26, 44, 0.75)`), dark mode palette, and CSS Grid.
- Icons provided by **Lucide React** (`lucide-react`).
- Data visualization powered by **D3.js** (`d3` force simulation).

### 4.2 Frontend Entrypoint & Component Tree
- [index.html](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/index.html): Imports Inter and JetBrains Mono fonts from Google Fonts.
- [main.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/main.jsx): Mounts `<App />` inside React StrictMode.
- [api.js](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/api.js): Centralized API client functions (`uploadFiles`, `startPipeline`, `loadSampleBatch`, `fetchProducts`, `fetchProduct`, `editField`, `approveRecord`, `fetchKnowledgeGraph`, `fetchEditHistory`).
- [App.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/App.jsx): Root dashboard orchestrating the 3-panel layout and bottom review bar:
  - **Header:** Brand icon, title, product selector dropdown, and manual refresh button.
  - **Left Panel (Ingestion & Pipeline):** `<UploadPanel />` and `<PipelineStatus />`.
  - **Center Panel (Structured Record):** `<ProductRecord />` and `<FieldCard />`.
  - **Right Panel (Knowledge Graph):** `<KnowledgeGraph />` and `<ConsistencyPanel />`.
  - **Bottom Bar (Human Review):** `<HumanReview />` and audit trail modals.

### 4.3 Component Breakdown
- [UploadPanel.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/UploadPanel.jsx): Drag-and-drop file upload zone supporting PDF/Image/CSV and prominent 1-click **"Load Sample Batch"** button.
- [PipelineStatus.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/PipelineStatus.jsx): Listens to SSE `/api/pipeline/status/{job_id}`, rendering animated stage badges (1-6) and progress bar.
- [ProductRecord.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/ProductRecord.jsx): Renders identity banner, overall score, core identity grid, technical specs grid, and native **Export JSON** and **Export CSV** download buttons.
- [FieldCard.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/FieldCard.jsx): Interactive field card displaying value, unit, citation count, and color-coded confidence badge (High=Emerald, Med=Amber, Low/Conflicted=Rose, Verified=Purple).
- [ProvenancePopup.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/ProvenancePopup.jsx): Modal window inspecting evidence receipts, extraction methods, locations, raw snippets, and conflict candidates.
- [KnowledgeGraph.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/KnowledgeGraph.jsx): Interactive D3.js force-directed graph rendering products, categories, and accessory nodes with drag/pan mechanics.
- [ConsistencyPanel.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/ConsistencyPanel.jsx): Displays catalog outlier warnings (e.g. weight anomaly alert).
- [HumanReview.jsx](file:///c:/Users/viswa/Desktop/SpectraAI/frontend/src/HumanReview.jsx): Displays review status, approval trigger button, field override modal, and full product edit history audit modal.

---

## 5. End-to-End Execution Trace

### Step 1: Ingestion & Source Registration
1. User clicks **"Load Sample Batch"** or drops files in `<UploadPanel />`.
2. Frontend issues `POST /api/demo/load-sample` or `POST /api/upload`.
3. `ingest.py:save_uploaded_file` computes SHA-256 hash (e.g. `csv_f6cab32e95d3`) and writes raw files to `backend/uploads/`.
4. Metadata is persisted to SQLite `sources` table via `database.save_source`.
5. Background task is spawned for `pipeline.run_product_intelligence_pipeline`.

### Step 2: Multimodal Extraction
1. `pipeline.py` iterates over registered `SourceDocument` records.
2. For each source, calls `extract.extract_from_pdf`, `extract.extract_from_image`, or `extract.extract_from_csv`.
3. In fallback mode:
   - PDF yields 8 attributes (`product_name`, `manufacturer`, `model_number`, `category`, `weight_kg=48.5kg`, `voltage=480V`, `description_long`, `certifications`).
   - Image yields 4 attributes (`model_number`, `voltage=460V`, `power_watts=15000W`, `sku`).
   - CSV yields 3 attributes (`product_name`, `model_number`, `country_of_origin`).

### Step 3: Multi-Source Merge & Conflict Detection
1. `merge.py:merge_extractions` groups attributes across sources.
2. Identical values (e.g. `model_number='VD-X500-480V-3P'`) receive confidence boost (0.90 + 0.08 = 0.98 -> capped at 1.0) and merged provenance receipts.
3. Conflicting values (`voltage`: PDF `480V` vs Image `460V`) trigger conflict scoring:
   - Primary value set to highest confidence candidate (`460V`, conf 0.91).
   - Confidence penalized by 0.7x (0.91 * 0.7 = `0.64`).
   - Status set to `conflicted`.
   - `conflict_candidates` populated with both candidates and their receipts.

### Step 4: RAG Enrichment & Taxonomy Mapping
1. `enrich.py:enrich_missing_fields` queries `EmbeddedRetriever`.
2. Missing warranty populated as `24 Months Standard Warranty` (`rag_enrichment`).
3. Category accessories populated from `category_taxonomies.json`.
4. Category mapped to UNSPSC `26101100 - Electric Motors` and ETIM `EC001851 (Electric Motor)`.
5. SEO Title synthesized: `Vortex Dynamics Tech UltraDrive X500 Industrial Inverter Motor 460V 15000W Model VD-X500-480V-3P`.

### Step 5: Knowledge Graph Reasoning
1. `knowledge_graph.py:add_product_to_graph` adds product node, category node, and accessory edges to NetworkX graph `G`.
2. `check_consistency` compares product specifications against sibling nodes (`prod_ref_101`, `prod_ref_102`).
3. `find_interchangeable_parts` matches sibling motors with equivalent voltage, scoring compatibility.

### Step 6: Business Rules Validation & CRI Scoring
1. `validate.py:validate_record` verifies numeric ranges.
2. Arithmetic mean of field confidences computed (`overall_confidence = 0.89`).
3. Because `voltage` is `conflicted`, `review_status` is assigned as `needs_review`.
4. Commerce Readiness Index calculated (`CRI = 92.0%`).
5. Product record saved to SQLite `products` table.

### Step 7: Human Review & Audit Logging
1. Reviewer inspects conflicting field in `<ProvenancePopup />`.
2. Reviewer clicks **"Correct / Override Field"** in `<HumanReview />`, submitting value `480V`, unit `V`.
3. Backend `human_review.log_human_edit` creates `human_correction` provenance, sets status to `human_verified`, confidence to `1.0`, records entry in SQLite `human_edits`, and re-evaluates record status.
4. Reviewer clicks **"Approve Record"**, setting status to `approved`.

### Step 8: Client Export
1. User clicks **"Export JSON"** or **"Export CSV"** in `<ProductRecord />`.
2. Browser directly compiles and downloads complete data records with full source citations.
