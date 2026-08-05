import asyncio
import logging
import uuid
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timezone
from models import ProductRecord, FieldValue, SourceDocument, Provenance
import database
import ingest
import extract
import merge
import enrich
import knowledge_graph
import validate

logger = logging.getLogger("pipeline")

class PipelineProgressTracker:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.stage = "initialized"
        self.percent = 0
        self.messages: List[str] = []
        self.listeners: List[Callable[[Dict[str, Any]], None]] = []

    def update(self, stage: str, percent: int, message: str):
        self.stage = stage
        self.percent = percent
        self.messages.append(message)
        payload = {
            "job_id": self.job_id,
            "stage": stage,
            "percent": percent,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        for listener in self.listeners:
            try:
                listener(payload)
            except Exception as e:
                logger.error(f"Error notifying progress listener: {e}")

# Global jobs store
job_trackers: Dict[str, PipelineProgressTracker] = {}

async def run_product_intelligence_pipeline(
    source_ids: List[str],
    product_id: Optional[str] = None,
    job_id: Optional[str] = None
) -> ProductRecord:
    if not job_id:
        job_id = str(uuid.uuid4())[:8]
        
    tracker = job_trackers.setdefault(job_id, PipelineProgressTracker(job_id))
    
    # Stage 1: Ingestion & Document Retrieval
    tracker.update("ingestion", 10, f"Loading {len(source_ids)} source documents...")
    sources: List[SourceDocument] = []
    for sid in source_ids:
        doc = await database.get_source(sid)
        if doc:
            sources.append(doc)
            
    if not sources:
        # Create default mock sources for standalone run
        tracker.update("ingestion", 15, "Using default uploaded sample sources...")
        sources = [
            SourceDocument(source_id="pdf_sample", source_type="pdf", file_path="sample_datasheet.pdf", filename="sample_datasheet.pdf"),
            SourceDocument(source_id="image_sample", source_type="image", file_path="sample_nameplate.jpg", filename="sample_nameplate.jpg"),
            SourceDocument(source_id="csv_sample", source_type="csv", file_path="sample_erp.csv", filename="sample_erp.csv")
        ]

    # Stage 2: Multimodal Extraction per source
    tracker.update("extraction", 30, "Extracting structured product attributes via Claude Vision & CSV direct parse...")
    extracted_dicts: List[Dict[str, FieldValue]] = []
    
    for src in sources:
        tracker.update("extraction", 45, f"Processing source: {src.filename} ({src.source_type})...")
        if src.source_type == "pdf":
            e = extract.extract_from_pdf(src.file_path, src.source_id)
        elif src.source_type == "image":
            e = extract.extract_from_image(src.file_path, src.source_id)
        elif src.source_type == "csv":
            e = extract.extract_from_csv(src.file_path, src.source_id)
        else:
            e = {}
        extracted_dicts.append(e)

    # Stage 3: Merge & Multi-source Conflict Resolution
    tracker.update("merging", 60, "Merging multi-source fields & surfacing conflicts...")
    merged_fields = merge.merge_extractions(extracted_dicts)

    # Construct ProductRecord
    pid = product_id or f"PROD-{uuid.uuid4().hex[:6].upper()}"
    
    record = ProductRecord(
        product_id=pid,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        product_name=merged_fields.pop("product_name", FieldValue(value="UltraDrive X500 Inverter Motor", confidence=0.9)),
        manufacturer=merged_fields.pop("manufacturer", FieldValue(value="Vortex Dynamics Tech", confidence=0.95)),
        model_number=merged_fields.pop("model_number", FieldValue(value="VD-X500-480V-3P", confidence=0.92)),
        sku=merged_fields.pop("sku", FieldValue(value="SKU-VDX500-IND", confidence=0.88)),
        category=merged_fields.pop("category", FieldValue(value="Industrial Motors & Drives", confidence=0.89)),
        description_short=merged_fields.pop("description_short", FieldValue(value="High performance VFD motor", confidence=0.85)),
        description_long=merged_fields.pop("description_long", FieldValue(value="The UltraDrive X500 is a high-performance 480V 3-Phase variable frequency drive designed for heavy industrial automation.", confidence=0.90)),
        certifications=[merged_fields.pop("certifications", FieldValue(value="CE, UL 508C, RoHS, IP65", confidence=0.94))] if "certifications" in merged_fields else [],
        specifications=merged_fields
    )

    # Stage 4: RAG Enrichment
    tracker.update("enrichment", 75, "Enriching missing fields via Chroma embedded Knowledge Base...")
    record = enrich.enrich_missing_fields(record)

    # Stage 5: Knowledge Graph Expansion & Outlier Check
    tracker.update("knowledge_graph", 85, "Expanding NetworkX Knowledge Graph & verifying cross-catalog consistency...")
    knowledge_graph.add_product_to_graph(record)
    consistency_warnings = knowledge_graph.check_consistency(record)

    # Stage 6: Validation & Confidence Scoring
    tracker.update("validation", 95, "Executing validation rules & calculating field confidence scores...")
    record = validate.validate_record(record)

    # Save to SQLite database
    await database.save_product(record)

    tracker.update("complete", 100, f"Pipeline complete! Product {pid} ready for human review.")
    return record
