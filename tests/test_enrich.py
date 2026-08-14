import pytest
from backend.enrich import retriever, enrich_missing_fields
from backend.models import ProductRecord, FieldValue

@pytest.mark.unit
def test_retriever_seed_documents_loaded():
    assert len(retriever.docs) >= 10

@pytest.mark.unit
def test_retriever_query_matching():
    matches = retriever.query("Industrial Motors", "warranty")
    assert len(matches) > 0
    assert any("motor" in m.get("content", "").lower() for m in matches)

@pytest.mark.unit
def test_enrich_missing_fields(sample_product):
    enriched = enrich_missing_fields(sample_product)
    assert enriched.unspsc_code is not None
    assert "26101100" in (enriched.unspsc_code.value or "")
    assert enriched.etim_class is not None
    assert "EC001851" in (enriched.etim_class.value or "")
    assert enriched.seo_title is not None
    assert "UltraDrive X500" in (enriched.seo_title.value or "")
    assert enriched.warranty is not None
    assert enriched.warranty.status == "enriched"
