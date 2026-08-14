import pytest
import backend.database as database

@pytest.mark.api
def test_root_endpoint(api_client):
    r = api_client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert "version" in data
    assert data["docs_url"] == "/docs"

@pytest.mark.api
def test_health_endpoint(api_client):
    r = api_client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "healthy"
    assert data["vlm_mode"] in ["live_claude", "fallback_demo"]

@pytest.mark.api
def test_upload_validation_rejects_empty(api_client):
    r = api_client.post("/api/upload", files=[])
    assert r.status_code in [400, 422]

@pytest.mark.api
def test_upload_validation_rejects_invalid_extension(api_client):
    r = api_client.post("/api/upload", files=[("files", ("bad.exe", b"bytes", "application/octet-stream"))])
    assert r.status_code == 400
    data = r.json()
    assert data.get("error_code") in ["INVALID_INPUT", "BAD_REQUEST", "INVALID_FILE_TYPE"]

@pytest.mark.api
def test_upload_validation_rejects_0_byte_file(api_client):
    r = api_client.post("/api/upload", files=[("files", ("empty.pdf", b"", "application/pdf"))])
    assert r.status_code == 400

@pytest.mark.api
def test_upload_valid_file(api_client):
    r = api_client.post("/api/upload", files=[("files", ("test.csv", b"col1,col2\na,b", "text/csv"))])
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert len(data["uploaded_sources"]) == 1

@pytest.mark.api
def test_unknown_product_returns_404_error_response(api_client):
    r = api_client.get("/api/products/NONEXISTENT_XYZ")
    assert r.status_code == 404
    data = r.json()
    assert data.get("error_code") == "NOT_FOUND"

@pytest.mark.api
def test_unknown_product_edit_returns_404(api_client):
    r = api_client.put("/api/products/NONEXISTENT_XYZ/fields/voltage", json={"value": "480V"})
    assert r.status_code == 404
    data = r.json()
    assert data.get("error_code") == "NOT_FOUND"

@pytest.mark.api
def test_unknown_product_approve_returns_404(api_client):
    r = api_client.post("/api/products/NONEXISTENT_XYZ/approve")
    assert r.status_code == 404
    data = r.json()
    assert data.get("error_code") == "NOT_FOUND"

@pytest.mark.api
def test_unknown_product_history_returns_404(api_client):
    r = api_client.get("/api/products/NONEXISTENT_XYZ/history")
    assert r.status_code == 404
    data = r.json()
    assert data.get("error_code") == "NOT_FOUND"

@pytest.mark.api
def test_pipeline_run_validation_empty_sources(api_client):
    r = api_client.post("/api/pipeline/run", json={"source_ids": []})
    assert r.status_code in [400, 422]

@pytest.mark.api
def test_cors_preflight(api_client):
    r = api_client.options(
        "/api/products",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
    )
    assert "access-control-allow-origin" in r.headers

@pytest.mark.api
def test_graph_export_endpoint(api_client):
    r = api_client.get("/api/graph")
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "links" in data
