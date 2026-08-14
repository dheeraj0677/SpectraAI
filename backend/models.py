from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, Dict, List, Any
from datetime import datetime, timezone

class Provenance(BaseModel):
    source_id: str              # which uploaded document/image/csv row
    source_type: Literal["pdf", "image", "csv", "rag_enrichment", "kg_inference", "human_correction"]
    location: Optional[str] = None   # e.g. "page 4, table 2" or "nameplate region top-left"
    extraction_method: str      # e.g. "claude-vision-extraction", "csv-direct", "rag-fill"
    confidence: float           # 0.0-1.0
    raw_snippet: Optional[str] = None  # short excerpt supporting this value

class FieldValue(BaseModel):
    value: Optional[Union[str, float, int, bool]] = None
    unit: Optional[str] = None
    confidence: float = 1.0
    provenance: List[Provenance] = Field(default_factory=list)
    status: Literal["extracted", "enriched", "conflicted", "human_verified", "missing", "needs_review"] = "missing"
    conflict_candidates: Optional[List[Dict[str, Any]]] = None  # if sources disagree

class ProductRecord(BaseModel):
    product_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Core identity
    product_name: FieldValue = Field(default_factory=FieldValue)
    manufacturer: FieldValue = Field(default_factory=FieldValue)
    model_number: FieldValue = Field(default_factory=FieldValue)
    sku: Optional[FieldValue] = None
    category: FieldValue = Field(default_factory=FieldValue)                # links to KG category node

    # Commerce-ready fields
    description_short: FieldValue = Field(default_factory=FieldValue)
    description_long: FieldValue = Field(default_factory=FieldValue)
    key_features: List[FieldValue] = Field(default_factory=list)

    # Industrial Taxonomy & E-Commerce Standards
    unspsc_code: Optional[FieldValue] = None
    etim_class: Optional[FieldValue] = None
    commerce_readiness_score: float = 0.0
    cri_breakdown: Dict[str, float] = Field(default_factory=dict)
    seo_title: Optional[FieldValue] = None
    interchangeable_parts: List[Dict[str, Any]] = Field(default_factory=list)

    # Technical specs (open-ended, category-dependent)
    specifications: Dict[str, FieldValue] = Field(default_factory=dict)   # e.g. {"voltage": FieldValue, "weight_kg": FieldValue}

    # Compliance / commerce
    certifications: List[FieldValue] = Field(default_factory=list)
    warranty: Optional[FieldValue] = None
    country_of_origin: Optional[FieldValue] = None

    # Relationships (Knowledge Graph edges)
    compatible_with: List[str] = Field(default_factory=list)      # product_ids
    replaces: Optional[str] = None
    accessories: List[str] = Field(default_factory=list)

    # Meta
    overall_confidence: float = 0.0
    review_status: Literal["pending", "approved", "needs_review", "rejected"] = "pending"
    human_edits_log: List[Dict[str, Any]] = Field(default_factory=list)

class SourceDocument(BaseModel):
    source_id: str
    source_type: Literal["pdf", "image", "csv"]
    file_path: str
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class PipelineRunRequest(BaseModel):
    source_ids: List[str]
    product_id: Optional[str] = None

class HumanEditRequest(BaseModel):
    value: Union[str, float, int, bool]
    unit: Optional[str] = None
    reviewer: str = "human_reviewer"
    reason: Optional[str] = "human_correction"
