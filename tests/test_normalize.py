import pytest
from backend.models import FieldValue, Provenance
from backend.normalize import canonicalize_field_name, normalize_field_value, parse_numeric_with_unit

@pytest.mark.unit
def test_canonicalize_field_names():
    assert canonicalize_field_name("rated_power") == "power_watts"
    assert canonicalize_field_name("operating_voltage") == "voltage"
    assert canonicalize_field_name("net_weight") == "weight_kg"
    assert canonicalize_field_name("brand") == "manufacturer"
    assert canonicalize_field_name("part_number") == "model_number"
    assert canonicalize_field_name("custom_spec") == "custom_spec"

@pytest.mark.unit
def test_power_normalization_kw_to_w():
    fv = FieldValue(
        value=15.0,
        unit="kW",
        provenance=[Provenance(source_id="s1", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm = normalize_field_value("power_watts", fv)
    assert norm.value == "15000W"
    assert norm.unit == "W"
    assert norm.provenance[0].raw_value == 15.0
    assert norm.provenance[0].raw_unit == "kW"
    assert "Converted 15.0 kW to Watts" in norm.provenance[0].normalization_rule

@pytest.mark.unit
def test_power_normalization_hp_to_w():
    fv = FieldValue(
        value=20.0,
        unit="HP",
        provenance=[Provenance(source_id="s2", source_type="image", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm = normalize_field_value("power_watts", fv)
    assert norm.value == "14914.0W"
    assert norm.unit == "W"

@pytest.mark.unit
def test_voltage_normalization():
    fv_kv = FieldValue(
        value=0.48,
        unit="kV",
        provenance=[Provenance(source_id="s3", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_kv = normalize_field_value("voltage", fv_kv)
    assert norm_kv.value == "480V"
    assert norm_kv.unit == "V"

    fv_clean = FieldValue(
        value="480V AC 3-Phase",
        unit=None,
        provenance=[Provenance(source_id="s4", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_clean = normalize_field_value("voltage", fv_clean)
    assert norm_clean.value == "480V"
    assert norm_clean.unit == "V"

@pytest.mark.unit
def test_weight_normalization():
    fv_lbs = FieldValue(
        value=106.9,
        unit="lbs",
        provenance=[Provenance(source_id="s5", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_lbs = normalize_field_value("weight_kg", fv_lbs)
    assert norm_lbs.value == 48.49
    assert norm_lbs.unit == "kg"

    fv_g = FieldValue(
        value=50000,
        unit="g",
        provenance=[Provenance(source_id="s6", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_g = normalize_field_value("weight_kg", fv_g)
    assert norm_g.value == 50.0
    assert norm_g.unit == "kg"

@pytest.mark.unit
def test_temperature_normalization():
    fv_f = FieldValue(
        value=104.0,
        unit="°F",
        provenance=[Provenance(source_id="s7", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_f = normalize_field_value("operating_temp", fv_f)
    assert norm_f.value == "40.0°C"
    assert norm_f.unit == "°C"

@pytest.mark.unit
def test_dimensions_normalization():
    fv_in = FieldValue(
        value=10.0,
        unit="inches",
        provenance=[Provenance(source_id="s8", source_type="pdf", location="P1", extraction_method="test", confidence=0.9)]
    )
    norm_in = normalize_field_value("dimensions_mm", fv_in)
    assert norm_in.value == 254.0
    assert norm_in.unit == "mm"
