import pytest
from pathlib import Path
from backend.extract import (
    extract_from_pdf_pypdf,
    fallback_pdf_extraction,
    fallback_image_extraction,
    extract_from_csv,
)

@pytest.mark.unit
def test_extract_from_pdf_pypdf_real_fixture():
    sample_pdf = Path("test_data/sample_datasheet.pdf")
    if sample_pdf.exists():
        fields = extract_from_pdf_pypdf(str(sample_pdf), "src_pdf_real")
        assert len(fields) >= 3
        assert "manufacturer" in fields
        assert fields["manufacturer"].is_synthetic is False
        assert fields["manufacturer"].observation_type == "directly_observed"
        assert fields["manufacturer"].provenance[0].extraction_method == "pypdf-text-extraction"

@pytest.mark.unit
def test_fallback_pdf_extraction():
    fields = fallback_pdf_extraction("dummy.pdf", "src_synth_pdf")
    assert "product_name" in fields
    assert "voltage" in fields
    assert fields["product_name"].is_synthetic is True
    assert fields["product_name"].observation_type == "heuristically_inferred"
    assert fields["product_name"].provenance[0].extraction_method == "synthetic-fallback-demo"

@pytest.mark.unit
def test_fallback_image_extraction_engineered_conflict():
    fields = fallback_image_extraction("dummy.jpg", "src_synth_img")
    assert "voltage" in fields
    assert fields["voltage"].value == "460V"
    assert fields["voltage"].is_synthetic is True
    assert fields["voltage"].observation_type == "heuristically_inferred"

@pytest.mark.unit
def test_extract_from_csv():
    sample_csv = Path("test_data/sample_erp_export.csv")
    if sample_csv.exists():
        fields = extract_from_csv(str(sample_csv), "src_csv_real")
        assert len(fields) >= 2
        assert "model_number" in fields
        assert fields["model_number"].is_synthetic is False
        assert fields["model_number"].observation_type == "directly_observed"
