# SpectraAI Pipeline Performance Benchmark Report

**Benchmark Type:** Deterministic Multimodal Pipeline Profiling  
**Timestamp:** 2026-08-14 12:27:15Z  
**Environment:** Python 3.13 / FastAPI Async SQLite Pipeline  
**Disclaimer:** *These metrics represent local technical execution timings on deterministic sample fixtures. Latency under live Claude API mode is subject to external network latency.*

---

## ⚡ Execution Summary

| Metric | Measured Value |
|---|---|
| **Iterations** | `5` |
| **Total Benchmark Time** | `67.37 ms` |
| **Average End-to-End Latency** | `13.26 ms` |
| **Peak Memory Allocation** | `0.154 MB` |
| **Local Processing Throughput** | `~74.22 records/sec` |

---

## ⏱️ Stage-by-Stage Latency Breakdown

| Pipeline Stage | Mean (ms) | Min (ms) | Max (ms) | Optimization Notes |
|---|---|---|---|---|
| **1. Ingestion & Hashes** | `4.63` | `3.69` | `5.18` | SHA-256 chunk hashing |
| **2. Multimodal Extraction** | `1.37` | `0.72` | `3.7` | Offline PDF `pypdf` / Fallback fixture parser |
| **3. Concordance & Merge** | `0.16` | `0.14` | `0.21` | Canonical aliasing & unit normalizer |
| **4. RAG Seed KB Enrichment** | `0.14` | `0.12` | `0.2` | In-memory token inverted index search |
| **5. NetworkX Graph Expansion** | `0.1` | `0.08` | `0.12` | Force graph nodes & sibling outlier check |
| **6. Business Rules & CRI Scoring** | `0.16` | `0.07` | `0.49` | 5-dimension scorecard scoring |

---

## 🛠️ Measured Bottlenecks & Applied Optimizations

1. **Database Query Indexing:**
   - Added SQLite index `idx_products_review_status ON products(review_status)` and `idx_human_edits_product_id ON human_edits(product_id)`, reducing list filtering overhead to `<0.5ms`.
2. **Seed KB In-Memory Caching:**
   - Loaded and indexed 14 seed JSON documents in memory once on startup rather than re-reading disk JSON per query.
3. **Non-Blocking Telemetry:**
   - Bound telemetry arrays to rolling size of 100 entries, preventing unbounded memory leak during prolonged server runs.
