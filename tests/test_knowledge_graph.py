import pytest
from backend.knowledge_graph import add_product_to_graph, check_consistency, find_interchangeable_parts, export_graph_json, G
from backend.models import ProductRecord, FieldValue

@pytest.mark.unit
def test_knowledge_graph_population(sample_product):
    initial_nodes = len(G.nodes)
    add_product_to_graph(sample_product)
    assert len(G.nodes) >= initial_nodes

@pytest.mark.unit
def test_consistency_check_normal(sample_product):
    warnings = check_consistency(sample_product)
    # Normal weight 48.5kg vs avg 46.4kg should not generate outlier warning
    assert len(warnings) == 0

@pytest.mark.unit
def test_consistency_check_outlier(sample_product):
    sample_product.specifications["weight_kg"] = FieldValue(value=5000.0, unit="kg", confidence=0.9)
    warnings = check_consistency(sample_product)
    assert len(warnings) > 0
    assert any("deviates significantly" in w.get("message", "") for w in warnings)

@pytest.mark.unit
def test_find_interchangeable_parts(sample_product):
    parts = find_interchangeable_parts(sample_product)
    assert isinstance(parts, list)
    assert len(parts) > 0

@pytest.mark.unit
def test_export_graph_json():
    data = export_graph_json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) > 0
