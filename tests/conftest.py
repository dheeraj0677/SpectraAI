import sys
import pytest
from pathlib import Path
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Ensure workspace root is on sys.path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import backend.database as database
from backend.main import app
from backend.models import ProductRecord, FieldValue, Provenance, SourceDocument

@pytest.fixture(autouse=True)
async def isolated_db(tmp_path, monkeypatch):
    """Provide an isolated temporary SQLite database for each test function."""
    temp_db_path = tmp_path / "test_product_intelligence.db"
    monkeypatch.setattr(database, "DB_PATH", temp_db_path)
    await database.init_db()
    yield temp_db_path
    if temp_db_path.exists():
        try:
            temp_db_path.unlink()
        except Exception:
            pass

@pytest.fixture
def sample_provenance():
    return Provenance(
        source_id="test_pdf_01",
        source_type="pdf",
        location="Page 1, Header",
        extraction_method="pypdf-text-extraction",
        confidence=0.92,
        raw_snippet="UltraDrive X500 Inverter Motor",
        is_synthetic=False,
        observation_type="directly_observed"
    )

@pytest.fixture
def sample_field_value(sample_provenance):
    return FieldValue(
        value="UltraDrive X500 Industrial Inverter Motor",
        confidence=0.92,
        provenance=[sample_provenance],
        status="extracted",
        is_synthetic=False,
        observation_type="directly_observed"
    )

@pytest.fixture
def sample_product(sample_field_value):
    return ProductRecord(
        product_id="TEST-PROD-001",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        product_name=sample_field_value,
        manufacturer=FieldValue(value="Vortex Dynamics Tech", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="VD-X500-480V-3P", confidence=0.90, status="extracted"),
        category=FieldValue(value="Industrial Motors & Drives", confidence=0.88, status="extracted"),
        specifications={
            "voltage": FieldValue(value="480V", unit="V", confidence=0.90, status="extracted"),
            "power_watts": FieldValue(value="15000W", unit="W", confidence=0.93, status="extracted"),
            "weight_kg": FieldValue(value=48.5, unit="kg", confidence=0.89, status="extracted")
        },
        overall_confidence=0.91,
        review_status="pending"
    )

@pytest.fixture
def api_client(isolated_db):
    """FastAPI TestClient fixture configured with isolated temporary database."""
    return TestClient(app)
