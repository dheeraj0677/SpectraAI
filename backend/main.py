import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
import uuid
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

import backend.database as database
import backend.ingest as ingest
import backend.pipeline as pipeline
import backend.human_review as human_review
import backend.knowledge_graph as knowledge_graph
import backend.enrich as enrich
import time
from backend.telemetry import telemetry
from backend.config import settings
from backend.models import (
    ProductRecord,
    HumanEditRequest,
    PipelineRunRequest,
    ErrorResponse,
    RootResponse,
    HealthCheckResponse,
    HealthDependencyStatus,
    DiagnosticsResponse,
    UploadResponse,
    DemoLoadResponse,
    PipelineRunResponse,
    ProductListResponse,
    ProductSummary,
    ProductDetailResponse,
    ProductEditResponse,
    ProductApproveResponse,
    EditHistoryResponse,
    EditHistoryEntry,
    KnowledgeGraphResponse,
    KnowledgeGraphNode,
    KnowledgeGraphLink,
    ConsistencyWarning,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialise DB and pre-seed demo product idempotently."""
    await database.init_db()
    logger.info("Database initialized successfully.")

    # Idempotent demo product seeding (configurable via PRESEED_DEMO_DATA)
    if settings.preseed_demo_data:
        demo_product = await database.get_product("PROD-DEMO-X500")
        if not demo_product:
            logger.info("Pre-seeding baseline demo product record (PROD-DEMO-X500)...")
            try:
                await pipeline.run_product_intelligence_pipeline(
                    source_ids=["pdf_demo", "image_demo", "csv_demo"],
                    product_id="PROD-DEMO-X500"
                )
            except Exception as e:
                logger.error(f"Error pre-seeding product: {e}")
        else:
            logger.info("Demo product (PROD-DEMO-X500) already exists. Skipping pre-seed.")

    yield  # Application runs here


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# ==============================================================================
# Correlation ID & Response Timing Middleware
# ==============================================================================
@app.middleware("http")
async def correlation_and_timing_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
    request.state.correlation_id = correlation_id
    t0 = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response

# ==============================================================================
# CORS Configuration
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# ==============================================================================
# Standardized Exception Handlers
# ==============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_code = "HTTP_ERROR"
    if exc.status_code == 404:
        error_code = "NOT_FOUND"
    elif exc.status_code == 400:
        error_code = "BAD_REQUEST"
    elif exc.status_code == 422:
        error_code = "VALIDATION_ERROR"
    elif exc.status_code == 413:
        error_code = "FILE_TOO_LARGE"

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=error_code,
            message=str(exc.detail),
            details=getattr(exc, "details", None)
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid request parameters or payload",
            details={"errors": exc.errors()}
        ).model_dump()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_code="INVALID_INPUT",
            message=str(exc)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred."
        ).model_dump()
    )

# ==============================================================================
# API Routes
# ==============================================================================

@app.get("/", response_model=RootResponse)
def read_root():
    """Root metadata & service health info."""
    return RootResponse(
        status="online",
        service=f"{settings.app_name} — Multimodal Product Intelligence",
        version=settings.app_version,
        docs_url="/docs"
    )

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Dependency readiness & subsystem health check without leaking credentials."""
    # 1. Check Database
    db_ok = await database.check_db_health()
    db_status = HealthDependencyStatus(
        status="healthy" if db_ok else "unhealthy",
        details="SQLite database connection operational" if db_ok else "SQLite database unreachable"
    )

    # 2. Check Knowledge Graph
    kg_nodes = len(knowledge_graph.G.nodes)
    kg_status = HealthDependencyStatus(
        status="healthy" if kg_nodes > 0 else "degraded",
        details=f"Knowledge Graph initialized with {kg_nodes} nodes"
    )

    # 3. Check Seed Knowledge Base
    kb_docs = len(enrich.retriever.docs)
    kb_status = HealthDependencyStatus(
        status="healthy" if kb_docs > 0 else "degraded",
        details=f"Seed KB initialized with {kb_docs} documents"
    )

    # Determine VLM operational mode (without revealing secret keys)
    vlm_mode = "live_claude" if settings.has_anthropic_key else "fallback_demo"

    overall_status = "healthy" if (db_ok and kg_nodes > 0 and kb_docs > 0) else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        version=settings.app_version,
        vlm_mode=vlm_mode,
        database=db_status,
        knowledge_graph=kg_status,
        seed_kb=kb_status
    )

@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and validate PDF, Image, or CSV sources for ingestion."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload")

    registered_sources = []
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file missing filename")

        contents = await file.read()
        try:
            source_doc = ingest.save_uploaded_file(contents, file.filename, file.content_type)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

        await database.save_source(source_doc)
        registered_sources.append(source_doc)

    return UploadResponse(status="success", uploaded_sources=registered_sources)

@app.post("/api/demo/load-sample", response_model=DemoLoadResponse)
async def load_sample_batch(background_tasks: BackgroundTasks):
    """Load pre-packaged multimodal sample batch (PDF + Image + CSV) and trigger pipeline."""
    sample_sources = [
        {"name": "datasheet_ultradrive_x500.pdf", "content": b"%PDF-1.5 UltraDrive X500 Industrial Inverter Motor Datasheet 480V 50kW"},
        {"name": "nameplate_motor_vfd.jpg", "content": b"NAMEPLATE IMAGE DATA 460V 5000W SKU-VD-X500"},
        {"name": "erp_catalog_export.csv", "content": b"product_name,manufacturer,model_number,sku\nUltraDrive X500,Vortex Dynamics Tech,VD-X500-480V-3P,SKU-VD-X500"}
    ]

    source_ids = []
    for sample in sample_sources:
        source_doc = ingest.save_uploaded_file(sample["content"], sample["name"])
        await database.save_source(source_doc)
        source_ids.append(source_doc.source_id)

    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(
        pipeline.run_product_intelligence_pipeline,
        source_ids=source_ids,
        product_id=f"PROD-SAMPLE-{job_id}",
        job_id=job_id
    )
    return DemoLoadResponse(status="started", job_id=job_id, sample_sources=source_ids)

@app.post("/api/pipeline/run", response_model=PipelineRunResponse)
async def run_pipeline(req: PipelineRunRequest, background_tasks: BackgroundTasks):
    """Trigger the end-to-end intelligence pipeline for given source IDs."""
    if not req.source_ids:
        raise HTTPException(status_code=400, detail="source_ids list cannot be empty")

    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(
        pipeline.run_product_intelligence_pipeline,
        source_ids=req.source_ids,
        product_id=req.product_id,
        job_id=job_id
    )
    return PipelineRunResponse(status="started", job_id=job_id)

@app.get("/api/pipeline/status/{job_id}")
async def pipeline_status_sse(job_id: str):
    """SSE endpoint streaming live progress and failure states of the pipeline."""
    async def event_generator():
        tracker = pipeline.job_trackers.get(job_id)
        if not tracker:
            yield f"data: {json.dumps({'error': 'Job not found', 'stage': 'failed'})}\n\n"
            return

        queue = asyncio.Queue()

        def listener(data):
            asyncio.create_task(queue.put(data))

        tracker.listeners.append(listener)

        try:
            # Emit current status immediately
            init_data = {
                "job_id": job_id,
                "stage": tracker.stage,
                "percent": tracker.percent,
                "message": tracker.messages[-1] if tracker.messages else "Starting pipeline...",
                "error": tracker.error
            }
            yield f"data: {json.dumps(init_data)}\n\n"

            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                    if data.get("stage") in ("complete", "failed"):
                        break
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'ping': True})}\n\n"
        finally:
            if listener in tracker.listeners:
                tracker.listeners.remove(listener)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/products", response_model=ProductListResponse)
async def list_all_products():
    """List all extracted product intelligence records."""
    products_data = await database.list_products()
    summaries = [
        ProductSummary(
            product_id=p["product_id"],
            product_name=p["product_name"] or "Unnamed Product",
            category=p["category"] or "Uncategorized",
            overall_confidence=p["overall_confidence"] or 0.0,
            review_status=p["review_status"] or "pending",
            updated_at=p["updated_at"]
        )
        for p in products_data
    ]
    return ProductListResponse(products=summaries)

@app.get("/api/products/{product_id}", response_model=ProductDetailResponse)
async def get_product_details(product_id: str):
    """Get complete product record including provenance, field values, and consistency warnings."""
    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Product record '{product_id}' not found")

    # Calculate consistency warnings from Knowledge Graph
    raw_warnings = knowledge_graph.check_consistency(record)
    typed_warnings = [
        ConsistencyWarning(
            field=w.get("field", "spec"),
            severity=w.get("severity", "warning"),
            message=w.get("message", ""),
            category_avg=w.get("category_avg"),
            current_value=w.get("current_value")
        )
        for w in raw_warnings
    ]

    detail_dict = record.model_dump()
    detail_dict["consistency_warnings"] = [w.model_dump() for w in typed_warnings]
    return ProductDetailResponse.model_validate(detail_dict)

@app.put("/api/products/{product_id}/fields/{field_name}", response_model=ProductEditResponse)
async def edit_product_field(product_id: str, field_name: str, edit_req: HumanEditRequest):
    """Human-in-the-loop field correction endpoint."""
    if not field_name or not field_name.strip():
        raise HTTPException(status_code=400, detail="Field name cannot be empty")

    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Product record '{product_id}' not found")

    updated_record = await human_review.log_human_edit(
        record=record,
        field_name=field_name.strip(),
        new_value=edit_req.value,
        unit=edit_req.unit,
        reviewer=edit_req.reviewer,
        reason=edit_req.reason or "human_correction"
    )
    telemetry.record_human_edit(1)

    # Update Knowledge Graph if core property changed
    knowledge_graph.add_product_to_graph(updated_record)

    return ProductEditResponse(status="updated", record=updated_record)

@app.post("/api/products/{product_id}/approve", response_model=ProductApproveResponse)
async def approve_product(product_id: str, reviewer: Optional[str] = "human_reviewer"):
    """Approve a product record."""
    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Product record '{product_id}' not found")

    approved_record = await human_review.approve_record(product_id, reviewer=reviewer or "human_reviewer")
    if not approved_record:
        raise HTTPException(status_code=404, detail=f"Product record '{product_id}' not found")

    telemetry.record_human_edit(1)
    return ProductApproveResponse(status="approved", record=approved_record)

@app.get("/api/products/{product_id}/history", response_model=EditHistoryResponse)
async def get_edit_history(product_id: str):
    """Get full human edit audit trail for a product."""
    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Product record '{product_id}' not found")

    raw_history = await database.get_product_edits(product_id)
    entries = [
        EditHistoryEntry(
            field_name=h["field_name"],
            old_value=h.get("old_value"),
            new_value=h.get("new_value"),
            reviewer=h.get("reviewer", "unknown"),
            timestamp=h.get("timestamp", ""),
            reason=h.get("reason")
        )
        for h in raw_history
    ]
    return EditHistoryResponse(product_id=product_id, edit_history=entries)

@app.get("/api/graph", response_model=KnowledgeGraphResponse)
def get_knowledge_graph():
    """Export NetworkX graph to D3 force graph format."""
    graph_data = knowledge_graph.export_graph_json()
    nodes = [KnowledgeGraphNode(**n) for n in graph_data.get("nodes", [])]
    links = [KnowledgeGraphLink(**l) for l in graph_data.get("links", [])]
    return KnowledgeGraphResponse(nodes=nodes, links=links)

@app.get("/api/diagnostics", response_model=DiagnosticsResponse)
async def get_diagnostics():
    """Retrieve live performance metrics, stage latency averages, and queue telemetry."""
    counts = await database.get_catalog_counts()
    graph_data = knowledge_graph.export_graph_json()
    vlm_mode = "live_claude" if settings.has_anthropic_key else "fallback_demo"

    snapshot = telemetry.get_diagnostics_snapshot(
        vlm_mode=vlm_mode,
        graph_nodes=len(graph_data.get("nodes", [])),
        graph_edges=len(graph_data.get("links", [])),
        review_queue_size=counts["pending_review"],
        approved_count=counts["approved"]
    )
    return DiagnosticsResponse(**snapshot)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
