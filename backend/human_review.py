from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from backend.models import ProductRecord, FieldValue, Provenance
import backend.database as database

async def log_human_edit(
    record: ProductRecord,
    field_name: str,
    new_value: Union[str, float, int, bool],
    unit: Optional[str] = None,
    reviewer: str = "human_reviewer",
    reason: str = "human_correction"
) -> ProductRecord:
    old_value = None
    
    # Check if field is in core identity or specifications
    if hasattr(record, field_name):
        curr_field: FieldValue = getattr(record, field_name)
        old_value = curr_field.value if curr_field else None
        
        prov = Provenance(
            source_id=f"human_review_{reviewer}",
            source_type="human_correction",
            location="Human Review Dashboard",
            extraction_method="human-edit",
            confidence=1.0,
            raw_snippet=f"Corrected by {reviewer}: '{old_value}' → '{new_value}'"
        )
        
        new_field = FieldValue(
            value=new_value,
            unit=unit or (curr_field.unit if curr_field else None),
            confidence=1.0,
            provenance=(curr_field.provenance if curr_field else []) + [prov],
            status="human_verified"
        )
        setattr(record, field_name, new_field)
    else:
        # Field in specifications dict
        if field_name in record.specifications:
            curr_field = record.specifications[field_name]
            old_value = curr_field.value
            prov_list = curr_field.provenance
            unit_val = unit or curr_field.unit
        else:
            prov_list = []
            unit_val = unit
            
        prov = Provenance(
            source_id=f"human_review_{reviewer}",
            source_type="human_correction",
            location="Human Review Dashboard",
            extraction_method="human-edit",
            confidence=1.0,
            raw_snippet=f"Corrected by {reviewer}: '{old_value}' → '{new_value}'"
        )
        
        record.specifications[field_name] = FieldValue(
            value=new_value,
            unit=unit_val,
            confidence=1.0,
            provenance=prov_list + [prov],
            status="human_verified"
        )

    # Record edit entry in human_edits_log list
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    edit_entry = {
        "field": field_name,
        "old_value": old_value,
        "new_value": new_value,
        "reviewer": reviewer,
        "timestamp": timestamp_iso,
        "reason": reason
    }
    record.human_edits_log.append(edit_entry)
    record.updated_at = datetime.now(timezone.utc)

    # Persist log entry in database
    await database.log_edit(
        product_id=record.product_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        reviewer=reviewer,
        timestamp=timestamp_iso,
        reason=reason
    )
    
    # Re-validate record status
    from backend.validate import validate_record
    record = validate_record(record)
    
    # Save updated product
    await database.save_product(record)
    return record

async def approve_record(product_id: str, reviewer: str = "human_reviewer") -> Optional[ProductRecord]:
    record = await database.get_product(product_id)
    if not record:
        return None
        
    record.review_status = "approved"
    record.updated_at = datetime.now(timezone.utc)
    
    await database.log_edit(
        product_id=record.product_id,
        field_name="review_status",
        old_value="pending",
        new_value="approved",
        reviewer=reviewer,
        timestamp=datetime.now(timezone.utc).isoformat(),
        reason="Record fully approved by reviewer"
    )
    
    await database.save_product(record)
    return record
