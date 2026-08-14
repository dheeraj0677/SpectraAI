# SpectraAI 🔬✨

> **Multimodal Product Intelligence — From Fragmented Data to Structured, Validated, Source-Cited Records**

SpectraAI ingests messy manufacturer data (PDF datasheets, nameplate photos, CSV exports) and produces commerce-ready product intelligence with per-field provenance, confidence scoring, conflict resolution, and human-in-the-loop audit trails.

---

## 🌟 The Demo Story

A judge hands you three inputs for one product:
1. A blurry photo of a **nameplate/spec sheet** (Image)
2. A messy **40-page PDF datasheet** with complex tables & diagrams
3. A partial **CSV row** from an ERP export (3 fields filled, 12 blank)

In under a minute, **SpectraAI**:
- Ingests all three sources with SHA-256 provenance hashes
- Extracts every product attribute via **Claude Vision (Sonnet)** with guaranteed structured JSON output
- Surfaces **multi-source conflicts** (e.g. nameplate says 460V, PDF says 480V) — never guesses silently
- Enriches missing attributes from a curated seed **RAG Knowledge Base**
- Expands an in-memory **NetworkX Knowledge Graph** and flags spec outliers
- Provides a **Human-in-the-Loop Dashboard** for field-level review with immutable audit trails

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   INGEST    │ --> │    EXTRACT       │ --> │    ENRICH        │ --> │   VALIDATE   │
│ PDF/Image/  │     │ (Claude Vision / │     │ (RAG + cross-ref │     │ (rules +     │
│ CSV upload  │     │  text extraction)│     │  + KG expansion) │     │  confidence) │
└─────────────┘     └──────────────────┘     └─────────────────┘     ───────┬──────┘
                                                                            │
                     ┌──────────────────┐     ┌─────────────────┐           │
                     │  HUMAN REVIEW    │ <-- │  MERGE/RESOLVE   │ <────────┘
                     │  (approve/edit)  │     │ (conflict scoring)│
                     └────────┬─────────┘     └─────────────────┘
                              │
                              v
                     ┌──────────────────┐
                     │  STRUCTURED       │
                     │  PRODUCT RECORD   │
                     │  + provenance log │
                     └──────────────────┘
```

---

## 📦 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python ≥3.12 (tested 3.13) + FastAPI + Pydantic v2 | Fast to write, Swagger UI as fallback demo |
| VLM | Claude Sonnet via `output_config.format` | Best-in-class vision + guaranteed JSON schema output |
| Orchestration | Custom ~200-line pipeline | No LangChain overhead — fast, transparent, debuggable |
| RAG | Embedded seed KB retriever | Small, curated, defensible — judges can ask "where did that come from?" |
| Knowledge Graph | NetworkX in-memory → D3 JSON export | Zero setup, full relationship modeling + outlier detection |
| Database | SQLite via aiosqlite | Product records + confidence + provenance + audit trail |
| Frontend | React + Vite + D3.js | Glassmorphism dark mode dashboard with force-directed graph |

---

## ⚡ Quickstart (Local — No Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
set ANTHROPIC_API_KEY=your-key-here   # Optional — smart fallback mode if absent
# Note: the anthropic package must be installed even in fallback mode (top-level import)
python main.py
```
→ API at `http://localhost:8000` | Swagger at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
→ Dashboard at `http://localhost:5173`

### One-Click (Windows)
- Double-click `run_backend.bat`
- Double-click `run_frontend.bat`

---

## 🎯 What We Explicitly Skipped (And Why)

| Skip | Reason |
|------|--------|
| Docker | Pure local execution — zero virtualization overhead |
| Multi-tenant Auth | Not needed for hackathon demo |
| Neo4j | NetworkX + D3 delivers the same visual impact with zero server setup |
| LangChain/LlamaIndex | Custom pipeline is faster to debug and demo |
| Production Vector DB | Embedded retriever is sufficient and fully explainable |

---

## ⚠️ Known Limitations

| Limitation | Detail |
|------------|--------|
| **Fallback mode** | Without `ANTHROPIC_API_KEY`, extraction returns hardcoded synthetic data for the UltraDrive X500 demo product. Real documents are not analysed. |
| **Test suite** | The 95-test E2E suite runs in fallback mode only. It does not validate live Claude API responses. |
| **chromadb** | Listed as a dependency in early versions but is **not used** — `enrich.py` uses an in-memory embedded retriever. Removed from `requirements.txt` in v1.1+. |
| **Single product** | The demo pipeline processes one product at a time. Batch processing endpoints exist but are not stress-tested. |
| **Python version** | Developed against Python ≥3.12. `datetime.utcnow()` was present in early commits; replaced with timezone-aware equivalents in v1.1+. |
