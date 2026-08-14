import pytest
from backend.models import FieldValue, Provenance
from backend.merge import merge_field, merge_extractions

@pytest.mark.unit
def test_merge_field_concordance_boosting():
    c1 = FieldValue(
        value="UltraDrive X500",
        confidence=0.92,
        provenance=[Provenance(source_id="s1", source_type="pdf", location="P1", extraction_method="pdf", confidence=0.92)],
        status="extracted",
        is_synthetic=False
    )
    c2 = FieldValue(
        value="UltraDrive X500",
        confidence=0.95,
        provenance=[Provenance(source_id="s2", source_type="csv", location="Row 1", extraction_method="csv", confidence=0.95)],
        status="extracted",
        is_synthetic=False
    )
    merged = merge_field("product_name", [c1, c2])
    assert merged.value == "UltraDrive X500"
    assert merged.confidence == 1.0  # 0.95 + 0.08 capped at 1.0
    assert merged.status == "extracted"
    assert len(merged.provenance) == 2
    assert merged.is_synthetic is False

@pytest.mark.unit
def test_merge_field_conflict_detection_and_penalty():
    c1 = FieldValue(
        value="480V",
        unit="V",
        confidence=0.90,
        provenance=[Provenance(source_id="s1", source_type="pdf", location="P3", extraction_method="pdf", confidence=0.90)],
        status="extracted",
        is_synthetic=True
    )
    c2 = FieldValue(
        value="460V",
        unit="V",
        confidence=0.92,
        provenance=[Provenance(source_id="s2", source_type="image", location="Plate", extraction_method="image", confidence=0.92)],
        status="extracted",
        is_synthetic=True
    )
    merged = merge_field("voltage", [c1, c2])
    assert merged.status == "conflicted"
    assert merged.observation_type == "conflicted"
    assert merged.confidence == pytest.approx(0.92 * 0.7, 0.01)
    assert merged.conflict_candidates is not None
    assert len(merged.conflict_candidates) == 2

@pytest.mark.unit
def test_merge_extractions_canonicalizes():
    s1 = {"rated_power": FieldValue(value="15000W", unit="W", confidence=0.9, status="extracted")}
    s2 = {"power_watts": FieldValue(value="15000W", unit="W", confidence=0.95, status="extracted")}
    merged = merge_extractions([s1, s2])
    assert "power_watts" in merged
    assert merged["power_watts"].status == "extracted"
