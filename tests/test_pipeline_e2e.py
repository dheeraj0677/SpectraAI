import pytest
from backend.pipeline import run_product_intelligence_pipeline, PipelineProgressTracker
from backend.human_review import log_human_edit, approve_record
import backend.database as database

@pytest.mark.e2e
async def test_full_pipeline_and_human_review_lifecycle(isolated_db):
    # 1. Run pipeline
    product = await run_product_intelligence_pipeline(
        source_ids=["pdf_sample", "image_sample", "csv_sample"],
        product_id="TEST-E2E-LIFECYCLE-01"
    )

    assert product is not None
    assert product.product_id == "TEST-E2E-LIFECYCLE-01"
    assert product.product_name.value is not None
    assert product.overall_confidence > 0.0
    assert product.review_status == "needs_review"

    # Engineered conflict on voltage
    assert "voltage" in product.specifications
    assert product.specifications["voltage"].status == "conflicted"
    assert len(product.specifications["voltage"].conflict_candidates) >= 2

    # 2. Human review edit
    updated = await log_human_edit(
        record=product,
        field_name="voltage",
        new_value="480V",
        unit="V",
        reviewer="senior_engineer",
        reason="Verified against physical inspection photo"
    )

    v_updated = updated.specifications["voltage"]
    assert v_updated.value == "480V"
    assert v_updated.status == "human_verified"
    assert v_updated.confidence == 1.0
    assert v_updated.observation_type == "human_verified"
    assert len(v_updated.provenance) > 1

    # 3. Approve record
    approved = await approve_record("TEST-E2E-LIFECYCLE-01", reviewer="senior_engineer")
    assert approved is not None
    assert approved.review_status == "approved"

    # 4. Check audit log in database
    edits = await database.get_product_edits("TEST-E2E-LIFECYCLE-01")
    assert len(edits) >= 2  # edit + approve

@pytest.mark.e2e
def test_job_tracker_failure_state():
    tracker = PipelineProgressTracker("test_job_fail")
    tracker.update("failed", 40, "Worker crash simulated", error="TestWorkerError")
    assert tracker.stage == "failed"
    assert tracker.error == "TestWorkerError"
    assert len(tracker.messages) > 0
