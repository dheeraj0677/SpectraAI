from typing import Dict, List, Any
from backend.models import FieldValue, Provenance, ProductRecord
from backend.normalize import canonicalize_field_name

def merge_field(field_name: str, candidates: List[FieldValue]) -> FieldValue:
    if not candidates:
        return FieldValue(status="missing")

    if len(candidates) == 1:
        return candidates[0]

    # Check if all candidate values match (converted to str for uniform comparison)
    values = {str(c.value).strip().lower() for c in candidates if c.value is not None}

    all_prov = []
    for c in candidates:
        all_prov.extend(c.provenance)

    all_synthetic = all(c.is_synthetic for c in candidates)

    if len(values) <= 1:
        # All sources agree! Boost confidence
        best_candidate = max(candidates, key=lambda c: c.confidence)
        merged_confidence = min(1.0, max(c.confidence for c in candidates) + 0.08)

        return FieldValue(
            value=best_candidate.value,
            unit=best_candidate.unit or next((c.unit for c in candidates if c.unit), None),
            confidence=merged_confidence,
            provenance=all_prov,
            status="extracted",
            is_synthetic=all_synthetic,
            observation_type="heuristically_inferred" if all_synthetic else "directly_observed"
        )
    else:
        # Genuine conflict detected across sources!
        best = max(candidates, key=lambda c: c.confidence)

        # Penalize confidence due to source conflict
        penalized_confidence = round(best.confidence * 0.7, 2)

        conflict_list = []
        for c in candidates:
            conflict_list.append({
                "value": c.value,
                "unit": c.unit,
                "confidence": c.confidence,
                "is_synthetic": c.is_synthetic,
                "observation_type": c.observation_type,
                "provenance": [p.model_dump() for p in c.provenance]
            })

        return FieldValue(
            value=best.value,
            unit=best.unit,
            confidence=penalized_confidence,
            provenance=all_prov,
            status="conflicted",
            conflict_candidates=conflict_list,
            is_synthetic=all_synthetic,
            observation_type="conflicted"
        )

def merge_extractions(extractions_by_source: List[Dict[str, FieldValue]]) -> Dict[str, FieldValue]:
    """Combines extractions from multiple sources (PDF, Image, CSV) into unified fields with canonical naming."""
    field_candidates: Dict[str, List[FieldValue]] = {}

    for source_dict in extractions_by_source:
        for fname, field_val in source_dict.items():
            canon_name = canonicalize_field_name(fname)
            if canon_name not in field_candidates:
                field_candidates[canon_name] = []
            field_candidates[canon_name].append(field_val)

    merged_fields = {}
    for fname, candidates in field_candidates.items():
        merged_fields[fname] = merge_field(fname, candidates)

    return merged_fields
