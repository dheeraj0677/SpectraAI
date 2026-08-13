import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
import uuid
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

import backend.database as database
import backend.ingest as ingest
import backend.pipeline as pipeline
import backend.human_review as human_review
import backend.knowledge_graph as knowledge_graph
from backend.models import ProductRecord, HumanEditRequest, PipelineRunRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="SpectraAI",
    description="SpectraAI — Multimodal product intelligence with source-cited extraction, RAG enrichment, knowledge graph reasoning, and human-in-the-loop audit trail.",
    version="1.0.0"
)

# Enable CORS for local dev server (Vite on port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await database.init_db()
    logger.info("Database initialized successfully.")
    
    # Pre-seed a initial demo product if database is empty
    products = await database.list_products()
    if not products:
        logger.info("Pre-seeding initial product record for instant demo readiness...")
        try:
            await pipeline.run_product_intelligence_pipeline(
                source_ids=["pdf_demo", "image_demo", "csv_demo"],
                product_id="PROD-DEMO-X500"
            )
        except Exception as e:
            logger.error(f"Error pre-seeding product: {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SpectraAI — Multimodal Product Intelligence",
        "docs_url": "/docs"
    }

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF, Image, or CSV sources for ingestion."""
    registered_sources = []
    for file in files:
        contents = await file.read()
        source_doc = ingest.save_uploaded_file(contents, file.filename)
        await database.save_source(source_doc)
        registered_sources.append(source_doc.model_dump())
    return {"status": "success", "uploaded_sources": registered_sources}

@app.post("/api/demo/load-sample")
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
    return {"status": "started", "job_id": job_id, "sample_sources": source_ids}

@app.post("/api/pipeline/run")
async def run_pipeline(req: PipelineRunRequest, background_tasks: BackgroundTasks):
    """Trigger the end-to-end intelligence pipeline."""
    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(
        pipeline.run_product_intelligence_pipeline,
        source_ids=req.source_ids,
        product_id=req.product_id,
        job_id=job_id
    )
    return {"status": "started", "job_id": job_id}

@app.get("/api/pipeline/status/{job_id}")
async def pipeline_status_sse(job_id: str):
    """SSE endpoint streaming live progress of the pipeline."""
    async def event_generator():
        tracker = pipeline.job_trackers.get(job_id)
        if not tracker:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return
            
        queue = asyncio.Queue()
        
        def listener(data):
            asyncio.create_task(queue.put(data))
            
        tracker.listeners.append(listener)
        
        # Emit current status immediately
        init_data = {
            "job_id": job_id,
            "stage": tracker.stage,
            "percent": tracker.percent,
            "message": tracker.messages[-1] if tracker.messages else "Starting pipeline...",
        }
        yield f"data: {json.dumps(init_data)}\n\n"
        
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("stage") == "complete":
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'ping': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/products")
async def list_all_products():
    """List all extracted product intelligence records."""
    products = await database.list_products()
    return {"products": products}

@app.get("/api/products/{product_id}")
async def get_product_details(product_id: str):
    """Get complete product record including provenance, field values, and status."""
    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product record not found")
    
    # Calculate consistency warnings from Knowledge Graph
    warnings = knowledge_graph.check_consistency(record)
    
    data = record.model_dump()
    data["consistency_warnings"] = warnings
    return data

@app.put("/api/products/{product_id}/fields/{field_name}")
async def edit_product_field(product_id: str, field_name: str, edit_req: HumanEditRequest):
    """Human-in-the-loop field correction endpoint."""
    record = await database.get_product(product_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product record not found")
        
    updated_record = await human_review.log_human_edit(
        record=record,
        field_name=field_name,
        new_value=edit_req.value,
        unit=edit_req.unit,
        reviewer=edit_req.reviewer,
        reason=edit_req.reason or "human_correction"
    )
    
    # Update Knowledge Graph if core property changed
    knowledge_graph.add_product_to_graph(updated_record)
    
    return {"status": "updated", "record": updated_record.model_dump()}

@app.post("/api/products/{product_id}/approve")
async def approve_product(product_id: str, reviewer: Optional[str] = "human_reviewer"):
    """Approve a product record."""
    approved_record = await human_review.approve_record(product_id, reviewer=reviewer or "human_reviewer")
    if not approved_record:
        raise HTTPException(status_code=404, detail="Product record not found")
    return {"status": "approved", "record": approved_record.model_dump()}

@app.get("/api/products/{product_id}/history")
async def get_edit_history(product_id: str):
    """Get full human edit audit trail for a product."""
    history = await database.get_product_edits(product_id)
    return {"product_id": product_id, "edit_history": history}

@app.get("/api/graph")
def get_knowledge_graph():
    """Export NetworkX graph to D3 force graph format."""
    return knowledge_graph.export_graph_json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
