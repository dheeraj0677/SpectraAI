import re
from typing import Dict, Any, Callable
from models import ProductRecord, FieldValue

# Rule definitions: field -> validation lambda or function returning bool
VALIDATION_RULES: Dict[str, Callable[[Any], bool]] = {
    "voltage": lambda v: check_voltage_sanity(v),
    "weight_kg": lambda v: check_numeric_range(v, 0.01, 50000.0),
    "power_watts": lambda v: check_numeric_range(v, 1.0, 1000000.0),
    "operating_temp": lambda v: True,
}

def check_numeric_range(val: Any, min_v: float, max_v: float) -> bool:
    try:
        if isinstance(val, (int, float)):
            return min_v <= val <= max_v
        # Parse numeric string
        num_match = re.search(r"[-+]?\d*\.\d+|\d+", str(val))
        if num_match:
            num = float(num_match.group())
            return min_v <= num <= max_v
        return True
    except Exception:
        return False

def check_voltage_sanity(val: Any) -> bool:
    try:
        num_match = re.search(r"\d+", str(val))
        if num_match:
            num = float(num_match.group())
            return 12 <= num <= 100000
        return True
    except Exception:
        return False

def validate_record(record: ProductRecord) -> ProductRecord:
    # 1. Validate individual spec fields
    for field_name, field_val in record.specifications.items():
        if field_val.status == "human_verified":
            continue
            
        if field_name in VALIDATION_RULES and field_val.value is not None:
            is_valid = VALIDATION_RULES[field_name](field_val.value)
            if not is_valid:
                field_val.status = "needs_review"
                field_val.confidence = round(field_val.confidence * 0.5, 2)

    # 2. Validate core fields
    core_fields = [
        record.product_name,
        record.manufacturer,
        record.model_number,
        record.category
    ]
    
    all_field_confidences = []
    for f in core_fields:
        if f.value is not None:
            all_field_confidences.append(f.confidence)
            
    for f in record.specifications.values():
        if f.value is not None:
            all_field_confidences.append(f.confidence)

    # 3. Overall confidence calculation
    if all_field_confidences:
        overall = sum(all_field_confidences) / len(all_field_confidences)
    else:
        overall = 0.5

    record.overall_confidence = round(overall, 2)
    
    # 4. Set review_status based on overall confidence & conflicted fields
    has_conflicts = any(f.status == "conflicted" for f in record.specifications.values())
    if record.review_status != "approved":
        if overall < 0.75 or has_conflicts:
            record.review_status = "needs_review"
        else:
            record.review_status = "pending"

    return record
