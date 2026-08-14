import pytest
from backend.telemetry import telemetry

@pytest.mark.unit
def test_telemetry_recording():
    telemetry.record_job_start()
    telemetry.record_stage_timing("ingestion", 5.2)
    telemetry.record_stage_timing("extraction", 12.8)
    telemetry.record_conflict_found(2)
    telemetry.record_enrichment_hit(3)
    telemetry.record_human_edit(1)

    assert telemetry.total_jobs >= 1
    assert telemetry.merge_conflicts_count >= 2
    assert telemetry.enrichment_hits_count >= 3
    assert telemetry.human_edits_count >= 1
    assert telemetry.get_average_timing("ingestion") > 0.0

@pytest.mark.api
def test_correlation_id_middleware(api_client):
    r = api_client.get("/", headers={"X-Correlation-ID": "test-corr-12345"})
    assert r.status_code == 200
    assert r.headers.get("X-Correlation-ID") == "test-corr-12345"
    assert "X-Response-Time-Ms" in r.headers

@pytest.mark.api
def test_diagnostics_endpoint(api_client):
    r = api_client.get("/api/diagnostics")
    assert r.status_code == 200
    data = r.json()
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert "pipeline_metrics" in data
    assert "average_stage_latencies_ms" in data
    assert "catalog_and_graph_status" in data
    assert data["vlm_mode"] in ["live_claude", "fallback_demo"]
