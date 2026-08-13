import re
from typing import Dict, Any, Callable
from backend.models import ProductRecord, FieldValue

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

    # 5. Commerce Readiness Index (CRI) Scorecard Calculation (0-100%)
    identity_score = 0.0
    if record.product_name and record.product_name.value: identity_score += 8.0
    if record.manufacturer and record.manufacturer.value: identity_score += 8.0
    if record.model_number and record.model_number.value: identity_score += 9.0

    specs_score = min(25.0, len(record.specifications) * 8.33)

    taxonomy_score = 0.0
    if record.category and record.category.value: taxonomy_score += 8.0
    if record.unspsc_code and record.unspsc_code.value: taxonomy_score += 6.0
    if record.etim_class and record.etim_class.value: taxonomy_score += 6.0

    content_score = 0.0
    if record.description_short and record.description_short.value: content_score += 5.0
    if record.description_long and record.description_long.value: content_score += 5.0
    if record.seo_title and record.seo_title.value: content_score += 5.0

    quality_score = 15.0
    if has_conflicts: quality_score -= 8.0
    if overall < 0.85: quality_score -= 5.0
    quality_score = max(0.0, quality_score)

    cri_total = round(identity_score + specs_score + taxonomy_score + content_score + quality_score, 1)
    record.commerce_readiness_score = min(100.0, max(0.0, cri_total))
    record.cri_breakdown = {
        "identity_completeness": round(identity_score, 1),
        "specifications_depth": round(specs_score, 1),
        "taxonomy_compliance": round(taxonomy_score, 1),
        "commerce_content": round(content_score, 1),
        "quality_and_accuracy": round(quality_score, 1)
    }

    return record
