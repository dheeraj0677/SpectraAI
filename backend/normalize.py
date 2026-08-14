import re
from typing import Optional, Tuple, Any, Dict
from backend.models import FieldValue, Provenance

# Canonical field name alias mappings
FIELD_NAME_ALIASES: Dict[str, str] = {
    "power": "power_watts",
    "power_w": "power_watts",
    "power_kw": "power_watts",
    "power_rating": "power_watts",
    "rated_power": "power_watts",
    "voltage": "voltage",
    "operating_voltage": "voltage",
    "rated_voltage": "voltage",
    "supply_voltage": "voltage",
    "volts": "voltage",
    "weight": "weight_kg",
    "net_weight": "weight_kg",
    "mass": "weight_kg",
    "weight_lbs": "weight_kg",
    "temp": "operating_temp",
    "temperature": "operating_temp",
    "temp_range": "operating_temp",
    "operating_temperature": "operating_temp",
    "name": "product_name",
    "title": "product_name",
    "item_name": "product_name",
    "brand": "manufacturer",
    "mfr": "manufacturer",
    "vendor": "manufacturer",
    "model": "model_number",
    "model_no": "model_number",
    "model_num": "model_number",
    "mpn": "model_number",
    "part_number": "model_number",
    "part_no": "model_number",
    "sku_code": "sku",
    "item_sku": "sku",
    "catalog_number": "sku",
    "product_category": "category",
    "taxonomy_category": "category",
}

def canonicalize_field_name(raw_name: str) -> str:
    """Normalize raw field names to snake_case canonical identifiers."""
    cleaned = raw_name.strip().lower().replace(" ", "_").replace("-", "_")
    return FIELD_NAME_ALIASES.get(cleaned, cleaned)

def parse_numeric_with_unit(raw_val: Any, explicit_unit: Optional[str] = None) -> Tuple[Optional[float], Optional[str]]:
    """Extract numeric quantity and unit suffix from value string or number."""
    if raw_val is None:
        return None, explicit_unit

    if isinstance(raw_val, (int, float)):
        return float(raw_val), (explicit_unit.strip() if explicit_unit else None)

    val_str = str(raw_val).strip()
    # Match pattern like: "15 kW", "15kW", "48.5 kg", "480V", "106.9 lbs"
    match = re.match(r"^([-+]?\d*\.?\d+)\s*([a-zA-Z°/%Ω]+.*)?$", val_str)
    if match:
        num = float(match.group(1))
        unit = match.group(2).strip() if match.group(2) else explicit_unit
        return num, unit

    return None, explicit_unit

def normalize_field_value(field_name: str, field_val: FieldValue) -> FieldValue:
    """
    Transparently normalizes units and formats for known technical specifications.
    Always records raw values, raw units, normalized values, normalized units,
    and the explicit transformation rule in the provenance receipt.
    """
    canon_name = canonicalize_field_name(field_name)
    raw_val = field_val.value
    raw_unit = field_val.unit

    if raw_val is None:
        return field_val

    normalized_val = raw_val
    normalized_unit = raw_unit
    conversion_rule = None

    num_val, inferred_unit = parse_numeric_with_unit(raw_val, raw_unit)
    unit_lower = (inferred_unit or raw_unit or "").lower().strip()

    # 1. Power Normalization (target: Watts / W)
    if canon_name in ("power_watts", "power"):
        if num_val is not None:
            if unit_lower in ("kw", "kilowatt", "kilowatts"):
                normalized_val = f"{int(num_val * 1000)}W" if (num_val * 1000).is_integer() else f"{num_val * 1000}W"
                normalized_unit = "W"
                conversion_rule = f"Converted {num_val} kW to Watts (* 1000)"
            elif unit_lower in ("hp", "horsepower"):
                w_val = round(num_val * 745.7, 1)
                normalized_val = f"{w_val}W"
                normalized_unit = "W"
                conversion_rule = f"Converted {num_val} HP to Watts (* 745.7)"
            elif unit_lower in ("w", "watts", "watt"):
                normalized_val = f"{int(num_val)}W" if num_val.is_integer() else f"{num_val}W"
                normalized_unit = "W"
                conversion_rule = "Standardized to Watt unit notation"

    # 2. Voltage Normalization (target: Volts / V)
    elif canon_name == "voltage":
        if num_val is not None:
            if unit_lower in ("kv", "kilovolt", "kilovolts"):
                v_val = int(num_val * 1000) if (num_val * 1000).is_integer() else num_val * 1000
                normalized_val = f"{v_val}V"
                normalized_unit = "V"
                conversion_rule = f"Converted {num_val} kV to Volts (* 1000)"
            elif unit_lower in ("mv", "millivolt", "millivolts"):
                v_val = num_val / 1000.0
                normalized_val = f"{v_val}V"
                normalized_unit = "V"
                conversion_rule = f"Converted {num_val} mV to Volts (/ 1000)"
            elif unit_lower.startswith("v") or "volt" in unit_lower or not unit_lower:
                v_val = int(num_val) if num_val.is_integer() else num_val
                normalized_val = f"{v_val}V"
                normalized_unit = "V"
                conversion_rule = "Standardized to Volt unit notation"

    # 3. Weight Normalization (target: kg)
    elif canon_name in ("weight_kg", "weight"):
        if num_val is not None:
            if unit_lower in ("lbs", "lb", "pound", "pounds"):
                kg_val = round(num_val * 0.453592, 2)
                normalized_val = kg_val
                normalized_unit = "kg"
                conversion_rule = f"Converted {num_val} lbs to kg (* 0.453592)"
            elif unit_lower in ("g", "grams", "gram"):
                kg_val = round(num_val / 1000.0, 3)
                normalized_val = kg_val
                normalized_unit = "kg"
                conversion_rule = f"Converted {num_val} g to kg (/ 1000)"
            elif unit_lower in ("kg", "kilograms", "kilogram"):
                normalized_val = num_val
                normalized_unit = "kg"
                conversion_rule = "Standardized to kg notation"

    # 4. Temperature Normalization (target: °C)
    elif canon_name in ("operating_temp", "temperature"):
        if num_val is not None and unit_lower in ("°f", "f", "deg f", "fahrenheit"):
            c_val = round((num_val - 32) * 5.0 / 9.0, 1)
            normalized_val = f"{c_val}°C"
            normalized_unit = "°C"
            conversion_rule = f"Converted {num_val}°F to Celsius ((F-32)*5/9)"

    # 5. Dimensions Normalization (target: mm)
    elif "dimension" in canon_name or "length" in canon_name or "width" in canon_name or "height" in canon_name:
        if num_val is not None:
            if unit_lower in ("in", "inch", "inches"):
                mm_val = round(num_val * 25.4, 1)
                normalized_val = mm_val
                normalized_unit = "mm"
                conversion_rule = f"Converted {num_val} inches to mm (* 25.4)"
            elif unit_lower in ("cm", "centimeters"):
                mm_val = round(num_val * 10.0, 1)
                normalized_val = mm_val
                normalized_unit = "mm"
                conversion_rule = f"Converted {num_val} cm to mm (* 10)"

    # Update provenance receipts with full transformation audit
    updated_prov = []
    for p in field_val.provenance:
        p_copy = p.model_copy()
        p_copy.raw_value = raw_val
        p_copy.raw_unit = raw_unit or inferred_unit
        p_copy.normalized_value = normalized_val
        p_copy.normalized_unit = normalized_unit
        p_copy.normalization_rule = conversion_rule
        updated_prov.append(p_copy)

    return FieldValue(
        value=normalized_val,
        unit=normalized_unit,
        confidence=field_val.confidence,
        provenance=updated_prov if updated_prov else field_val.provenance,
        status=field_val.status,
        conflict_candidates=field_val.conflict_candidates,
        is_synthetic=field_val.is_synthetic,
        observation_type=field_val.observation_type
    )
