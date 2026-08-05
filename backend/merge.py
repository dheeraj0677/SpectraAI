from typing import Dict, List, Any
from models import FieldValue, Provenance, ProductRecord

def merge_field(field_name: str, candidates: List[FieldValue]) -> FieldValue:
    if not candidates:
        return FieldValue(status="missing")
        
    if len(candidates) == 1:
        return candidates[0]
        
    # Check if all candidate values match (converted to str for uniform comparison)
    values = {str(c.value).strip().lower() for c in candidates if c.value is not None}
    
    if len(values) <= 1:
        # All sources agree! Boost confidence
        best_candidate = max(candidates, key=lambda c: c.confidence)
        merged_confidence = min(1.0, max(c.confidence for c in candidates) + 0.08)
        
        # Combine all provenance traces
        all_prov = []
        for c in candidates:
            all_prov.extend(c.provenance)
            
        return FieldValue(
            value=best_candidate.value,
            unit=best_candidate.unit or next((c.unit for c in candidates if c.unit), None),
            confidence=merged_confidence,
            provenance=all_prov,
            status="extracted"
        )
    else:
        # Genuine conflict detected across sources!
        best = max(candidates, key=lambda c: c.confidence)
        all_prov = []
        for c in candidates:
            all_prov.extend(c.provenance)

        # Penalize confidence due to source conflict
        penalized_confidence = round(best.confidence * 0.7, 2)
        
        conflict_list = []
        for c in candidates:
            conflict_list.append({
                "value": c.value,
                "unit": c.unit,
                "confidence": c.confidence,
                "provenance": [p.model_dump() for p in c.provenance]
            })

        return FieldValue(
            value=best.value,
            unit=best.unit,
            confidence=penalized_confidence,
            provenance=all_prov,
            status="conflicted",
            conflict_candidates=conflict_list
        )

def merge_extractions(extractions_by_source: List[Dict[str, FieldValue]]) -> Dict[str, FieldValue]:
    """Combines extractions from multiple sources (PDF, Image, CSV) into unified fields."""
    field_candidates: Dict[str, List[FieldValue]] = {}
    
    for source_dict in extractions_by_source:
        for fname, field_val in source_dict.items():
            if fname not in field_candidates:
                field_candidates[fname] = []
            field_candidates[fname].append(field_val)

    merged_fields = {}
    for fname, candidates in field_candidates.items():
        merged_fields[fname] = merge_field(fname, candidates)

    return merged_fields
