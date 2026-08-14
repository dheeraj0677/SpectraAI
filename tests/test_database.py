import pytest
from datetime import datetime, timezone
import backend.database as database
from backend.models import SourceDocument, ProductRecord, FieldValue

@pytest.mark.integration
async def test_database_health_check(isolated_db):
    is_healthy = await database.check_db_health()
    assert is_healthy is True

@pytest.mark.integration
async def test_save_and_get_source(isolated_db):
    src = SourceDocument(
        source_id="src_test_123",
        source_type="pdf",
        file_path="uploads/test.pdf",
        filename="test.pdf",
        uploaded_at=datetime.now(timezone.utc)
    )
    await database.save_source(src)
    retrieved = await database.get_source("src_test_123")
    assert retrieved is not None
    assert retrieved.filename == "test.pdf"
    assert retrieved.source_type == "pdf"

@pytest.mark.integration
async def test_save_and_get_product(isolated_db, sample_product):
    await database.save_product(sample_product)
    retrieved = await database.get_product(sample_product.product_id)
    assert retrieved is not None
    assert retrieved.product_id == sample_product.product_id
    assert retrieved.product_name.value == sample_product.product_name.value

@pytest.mark.integration
async def test_list_products(isolated_db, sample_product):
    await database.save_product(sample_product)
    products = await database.list_products()
    assert len(products) >= 1
    assert any(p["product_id"] == sample_product.product_id for p in products)

@pytest.mark.integration
async def test_log_and_get_edits(isolated_db):
    await database.log_edit(
        product_id="P-EDIT-TEST",
        field_name="voltage",
        old_value="460V",
        new_value="480V",
        reviewer="quality_eng",
        timestamp=datetime.now(timezone.utc).isoformat(),
        reason="Visual check"
    )
    edits = await database.get_product_edits("P-EDIT-TEST")
    assert len(edits) == 1
    assert edits[0]["field_name"] == "voltage"
    assert edits[0]["old_value"] == "460V"
    assert edits[0]["new_value"] == "480V"
    assert edits[0]["reviewer"] == "quality_eng"
