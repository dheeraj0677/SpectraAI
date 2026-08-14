# SpectraAI API Contract & Specification

> **Base URL:** `http://localhost:8000`  
> **OpenAPI Documentation:** [`/docs`](http://localhost:8000/docs) (Swagger UI) | [`/redoc`](http://localhost:8000/redoc) (ReDoc)  
> **API Version:** `1.0.0`  
> **Protocol:** HTTP/1.1 with Server-Sent Events (SSE)

---

## 1. Standard Error Response Model

All API endpoints return structured JSON errors adhering to the `ErrorResponse` schema whenever an error occurs (HTTP 4xx and 5xx).

```json
{
  "error_code": "NOT_FOUND",
  "message": "Product record 'PROD-UNKNOWN' not found",
  "details": null
}
```

### 1.1 Error Codes Reference

| Error Code | HTTP Status | Description |
|---|---|---|
| `NOT_FOUND` | 404 | The requested product, job, or resource does not exist. |
| `VALIDATION_ERROR` | 422 | Request body or query parameters failed Pydantic schema validation. |
| `INVALID_INPUT` | 400 | A parameter or upload failed business/format validation (e.g. empty field name). |
| `INVALID_FILE_TYPE` | 400 | An uploaded file has an unsupported extension (allowed: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff`, `.csv`). |
| `FILE_TOO_LARGE` | 400 / 413 | An uploaded file exceeds `MAX_UPLOAD_SIZE_BYTES` (default: 50MB). |
| `EMPTY_FILE` | 400 | An uploaded file contains 0 bytes. |
| `INTERNAL_SERVER_ERROR` | 500 | An unexpected server error occurred (stack traces are logged, never leaked). |

---

## 2. CORS & Security Policy

- **Configurable Origins:** Driven by `CORS_ORIGINS` environment variable (defaults to `http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000`).
- **Allowed Methods:** `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`, `HEAD`.
- **Allowed Headers:** `*` (standard headers: `Content-Type`, `Authorization`, `Accept`, `X-Requested-With`).
- **Credentials:** `allow_credentials=True` enabled for local developer proxying.
- **Credential Masking:** `ANTHROPIC_API_KEY` is strictly masked and never returned in health checks or serialized models.

---

## 3. Endpoints Specification

### 3.1 `GET /` — Root Service Metadata
Returns high-level service status and link to interactive documentation.

- **Response (200 OK):** `RootResponse`
  ```json
  {
    "status": "online",
    "service": "SpectraAI — Multimodal Product Intelligence",
    "version": "1.0.0",
    "docs_url": "/docs"
  }
  ```

---

### 3.2 `GET /api/health` — Subsystem & Dependency Health Check
Reports readiness of SQLite database, Knowledge Graph, Seed KB, and VLM operational mode without leaking credentials.

- **Response (200 OK):** `HealthCheckResponse`
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2026-08-14T12:00:00Z",
    "vlm_mode": "fallback_demo",
    "database": {
      "status": "healthy",
      "details": "SQLite database connection operational"
    },
    "knowledge_graph": {
      "status": "healthy",
      "details": "Knowledge Graph initialized with 8 nodes"
    },
    "seed_kb": {
      "status": "healthy",
      "details": "Seed KB initialized with 13 documents"
    }
  }
  ```

---

### 3.3 `POST /api/upload` — Multimodal Source Ingestion
Accepts one or more raw files (PDF, image, CSV), enforces size and extension validation, generates SHA-256 hashes, and registers sources.

- **Content-Type:** `multipart/form-data`
- **Request Body:** Form parameter `files`: List of binary files.
- **Response (200 OK):** `UploadResponse`
  ```json
  {
    "status": "success",
    "uploaded_sources": [
      {
        "source_id": "pdf_a1b2c3d4e5f6",
        "source_type": "pdf",
        "file_path": ".../backend/uploads/pdf_a1b2c3d4e5f6_datasheet.pdf",
        "filename": "datasheet.pdf",
        "uploaded_at": "2026-08-14T12:00:00Z"
      }
    ]
  }
  ```
- **Error Responses:**
  - `400 Bad Request` (`INVALID_INPUT` / `INVALID_FILE_TYPE` / `EMPTY_FILE`): If files list is empty, contains unsupported extensions, or file is 0 bytes.

---

### 3.4 `POST /api/demo/load-sample` — Sample Multimodal Batch Trigger
Triggers a synthetic batch (datasheet PDF + motor nameplate JPG + ERP CSV) in a background task for instant demonstration.

- **Response (200 OK):** `DemoLoadResponse`
  ```json
  {
    "status": "started",
    "job_id": "a1b2c3d4",
    "sample_sources": ["pdf_...", "image_...", "csv_..."]
  }
  ```

---

### 3.5 `POST /api/pipeline/run` — Run Intelligence Pipeline
Triggers the 6-stage async intelligence pipeline for a list of registered `source_ids`.

- **Content-Type:** `application/json`
- **Request Body:** `PipelineRunRequest`
  ```json
  {
    "source_ids": ["pdf_a1b2c3d4e5f6", "image_f6e5d4c3b2a1"],
    "product_id": "PROD-CUSTOM-001"
  }
  ```
- **Response (200 OK):** `PipelineRunResponse`
  ```json
  {
    "status": "started",
    "job_id": "b2c3d4e5"
  }
  ```
- **Error Responses:**
  - `422 Unprocessable Entity` (`VALIDATION_ERROR`): If `source_ids` is missing or empty.

---

### 3.6 `GET /api/pipeline/status/{job_id}` — Live Pipeline SSE Stream
Streams Server-Sent Events (SSE) broadcasting real-time progress percentages, stages, and status messages.

- **Content-Type:** `text/event-stream`
- **Event Data Schema:**
  ```json
  {
    "job_id": "b2c3d4e5",
    "stage": "extraction",
    "percent": 45,
    "message": "Processing source: nameplate.jpg (image)...",
    "error": null,
    "timestamp": "2026-08-14T12:00:05Z"
  }
  ```
- **Stages:** `ingestion` (10%) → `extraction` (30-45%) → `merging` (60%) → `enrichment` (75%) → `knowledge_graph` (85%) → `validation` (95%) → `complete` (100%) or `failed`.

---

### 3.7 `GET /api/products` — List Product Records
Returns summary metadata for all processed catalog records.

- **Response (200 OK):** `ProductListResponse`
  ```json
  {
    "products": [
      {
        "product_id": "PROD-DEMO-X500",
        "product_name": "UltraDrive X500 Industrial Inverter Motor",
        "category": "Industrial Motors & Drives",
        "overall_confidence": 0.89,
        "review_status": "needs_review",
        "updated_at": "2026-08-14T12:00:00Z"
      }
    ]
  }
  ```

---

### 3.8 `GET /api/products/{product_id}` — Product Details & Consistency Warnings
Retrieves full structured product intelligence including field-level provenance citations, conflict candidate arrays, and knowledge graph outlier warnings.

- **Response (200 OK):** `ProductDetailResponse`
  ```json
  {
    "product_id": "PROD-DEMO-X500",
    "product_name": {
      "value": "UltraDrive X500 Industrial Inverter Motor",
      "confidence": 0.92,
      "status": "extracted",
      "provenance": [...]
    },
    "specifications": {
      "voltage": {
        "value": "460V",
        "unit": "V",
        "confidence": 0.64,
        "status": "conflicted",
        "conflict_candidates": [...]
      }
    },
    "commerce_readiness_score": 92.0,
    "cri_breakdown": {...},
    "consistency_warnings": [
      {
        "field": "weight_kg",
        "severity": "warning",
        "message": "Weight (5000.0 kg) deviates significantly from category average...",
        "category_avg": 46.4,
        "current_value": 5000.0
      }
    ]
  }
  ```
- **Error Responses:**
  - `404 Not Found` (`NOT_FOUND`): If `product_id` does not exist.

---

### 3.9 `PUT /api/products/{product_id}/fields/{field_name}` — Field Override & Audit
Applies a human review correction to a specific field, elevates field status to `human_verified`, attaches a `human_correction` receipt, re-evaluates validation, and persists to SQLite.

- **Content-Type:** `application/json`
- **Request Body:** `HumanEditRequest`
  ```json
  {
    "value": "480V",
    "unit": "V",
    "reviewer": "quality_engineer",
    "reason": "Verified against physical nameplate high-res photo"
  }
  ```
- **Response (200 OK):** `ProductEditResponse`
  ```json
  {
    "status": "updated",
    "record": {...}
  }
  ```
- **Error Responses:**
  - `404 Not Found` (`NOT_FOUND`): If `product_id` is unknown.
  - `400 Bad Request` (`INVALID_INPUT`): If `field_name` is blank.

---

### 3.10 `POST /api/products/{product_id}/approve` — Approve Product Record
Marks a product record as fully approved and records an approval entry in the audit trail.

- **Query Parameters:** `reviewer` (optional string, default: `"human_reviewer"`).
- **Response (200 OK):** `ProductApproveResponse`
  ```json
  {
    "status": "approved",
    "record": {...}
  }
  ```
- **Error Responses:**
  - `404 Not Found` (`NOT_FOUND`): If `product_id` is unknown.

---

### 3.11 `GET /api/products/{product_id}/history` — Edit History Audit Trail
Retrieves the complete immutable audit trail of human corrections and approvals.

- **Response (200 OK):** `EditHistoryResponse`
  ```json
  {
    "product_id": "PROD-DEMO-X500",
    "edit_history": [
      {
        "field_name": "voltage",
        "old_value": "460V",
        "new_value": "480V",
        "reviewer": "quality_engineer",
        "timestamp": "2026-08-14T12:05:00Z",
        "reason": "Verified against physical nameplate high-res photo"
      }
    ]
  }
  ```
- **Error Responses:**
  - `404 Not Found` (`NOT_FOUND`): If `product_id` is unknown.

---

### 3.12 `GET /api/graph` — Knowledge Graph Topology Export
Exports the NetworkX directed graph in D3 force-directed JSON format.

- **Response (200 OK):** `KnowledgeGraphResponse`
  ```json
  {
    "nodes": [
      {"id": "PROD-DEMO-X500", "label": "UltraDrive X500...", "type": "product", "category": "Industrial Motors & Drives"},
      {"id": "Industrial Motors & Drives", "label": "Industrial Motors & Drives", "type": "category"}
    ],
    "links": [
      {"source": "PROD-DEMO-X500", "target": "Industrial Motors & Drives", "relation": "belongs_to"}
    ]
  }
  ```
