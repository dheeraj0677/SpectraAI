import pytest
from datetime import datetime, timezone
from backend.models import (
    Provenance,
    FieldValue,
    ProductRecord,
    SourceDocument,
    ErrorResponse,
    HealthCheckResponse,
    HealthDependencyStatus,
    PipelineRunRequest,
    HumanEditRequest,
)

@pytest.mark.unit
def test_provenance_model_instantiation():
    p = Provenance(
        source_id="pdf_abc123",
        source_type="pdf",
        location="Page 3, Table 2",
        extraction_method="claude-vision-extraction",
        confidence=0.92,
        raw_snippet="Model: VD-X500-480V-3P",
        is_synthetic=False,
        observation_type="directly_observed"
    )
    assert p.source_id == "pdf_abc123"
    assert p.source_type == "pdf"
    assert p.confidence == 0.92
    assert p.is_synthetic is False
    assert p.observation_type == "directly_observed"

@pytest.mark.unit
def test_field_value_statuses():
    for status in ["extracted", "enriched", "conflicted", "human_verified", "missing", "needs_review"]:
        fv = FieldValue(value="test", confidence=0.8, status=status)
        assert fv.status == status

@pytest.mark.unit
def test_field_value_types():
    for val, expected_type in [(42, int), (3.14, float), ("hello", str), (True, bool), (None, type(None))]:
        fv = FieldValue(value=val, confidence=0.9)
        assert isinstance(fv.value, expected_type)

@pytest.mark.unit
def test_product_record_serialization_roundtrip(sample_product):
    json_str = sample_product.model_dump_json()
    assert len(json_str) > 0
    reconstructed = ProductRecord.model_validate_json(json_str)
    assert reconstructed.product_id == sample_product.product_id
    assert reconstructed.product_name.value == sample_product.product_name.value
    assert reconstructed.overall_confidence == sample_product.overall_confidence

@pytest.mark.unit
def test_error_response_model():
    err = ErrorResponse(
        error_code="NOT_FOUND",
        message="Product not found",
        details={"product_id": "UNKNOWN"}
    )
    assert err.error_code == "NOT_FOUND"
    assert err.message == "Product not found"
    assert err.details == {"product_id": "UNKNOWN"}

@pytest.mark.unit
def test_health_check_model():
    h = HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        vlm_mode="fallback_demo",
        database=HealthDependencyStatus(status="healthy", details="SQLite OK"),
        knowledge_graph=HealthDependencyStatus(status="healthy", details="Nodes OK"),
        seed_kb=HealthDependencyStatus(status="healthy", details="Docs OK")
    )
    assert h.status == "healthy"
    assert h.vlm_mode == "fallback_demo"
    assert h.database.status == "healthy"
