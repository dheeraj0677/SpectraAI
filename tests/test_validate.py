import pytest
from backend.validate import check_voltage_sanity, check_numeric_range, validate_record
from backend.models import FieldValue, ProductRecord

@pytest.mark.unit
def test_validate_voltage_sanity():
    assert check_voltage_sanity("480V") is True
    assert check_voltage_sanity("12V") is True
    assert check_voltage_sanity("0V") is False

@pytest.mark.unit
def test_validate_numeric_range():
    assert check_numeric_range(48.5, 0.01, 50000.0) is True
    assert check_numeric_range("48.5 kg", 0.01, 50000.0) is True
    assert check_numeric_range(-5.0, 0.01, 50000.0) is False

@pytest.mark.unit
def test_validate_record_confidence_and_cri(sample_product):
    validated = validate_record(sample_product)
    assert 0.0 < validated.overall_confidence <= 1.0
    assert 0.0 < validated.commerce_readiness_score <= 100.0
    assert "identity_completeness" in validated.cri_breakdown
    assert "specifications_depth" in validated.cri_breakdown
    assert validated.review_status in ["pending", "needs_review", "approved"]
