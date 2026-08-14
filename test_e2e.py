"""
End-to-end test script for AI Product Intelligence Engine.
Tests all pipeline stages: ingestion, extraction, merge/conflict, enrichment,
knowledge graph, validation, human review, and audit logging.

Run with: python test_e2e.py
"""
import sys
import os
import io
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# ────────────────────────────────────────────────────────────────
# Test utilities
# ────────────────────────────────────────────────────────────────
PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
results = []

def record(test_name, passed, detail=""):
    status = PASS if passed else FAIL
    results.append({"test": test_name, "status": status, "detail": detail})
    print(f"  {status}  {test_name}" + (f"  ({detail})" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ────────────────────────────────────────────────────────────────
# 1. DATA MODEL TESTS
# ────────────────────────────────────────────────────────────────
def test_data_models():
    section("1. PYDANTIC DATA MODEL VALIDATION")
    from backend.models import Provenance, FieldValue, ProductRecord, SourceDocument

    # Test Provenance creation
    try:
        p = Provenance(
            source_id="pdf_abc123",
            source_type="pdf",
            location="Page 3, Table 2",
            extraction_method="claude-vision-extraction",
            confidence=0.92,
            raw_snippet="Model: VD-X500-480V-3P"
        )
        record("Provenance model instantiation", True, f"source_id={p.source_id}")
    except Exception as e:
        record("Provenance model instantiation", False, str(e))

    # Test FieldValue with all statuses
    for status in ["extracted", "enriched", "conflicted", "human_verified", "missing", "needs_review"]:
        try:
            fv = FieldValue(value="test", confidence=0.8, status=status)
            record(f"FieldValue status='{status}'", True)
        except Exception as e:
            record(f"FieldValue status='{status}'", False, str(e))

    # Test FieldValue with different value types
    for val, label in [(42, "int"), (3.14, "float"), ("hello", "str"), (True, "bool"), (None, "None")]:
        try:
            fv = FieldValue(value=val, confidence=0.9)
            record(f"FieldValue value type={label}", True, f"value={fv.value}")
        except Exception as e:
            record(f"FieldValue value type={label}", False, str(e))

    # Test full ProductRecord
    try:
        pr = ProductRecord(
            product_id="TEST-001",
            product_name=FieldValue(value="Test Product", confidence=0.9, status="extracted"),
            manufacturer=FieldValue(value="Test Corp", confidence=0.95, status="extracted"),
            model_number=FieldValue(value="TC-100", confidence=0.88, status="extracted"),
            category=FieldValue(value="Test Category", confidence=0.85, status="extracted"),
            description_short=FieldValue(value="A test product", confidence=0.8),
            description_long=FieldValue(value="A longer test product description", confidence=0.8),
            specifications={
                "voltage": FieldValue(value="480V", unit="V", confidence=0.9, status="extracted"),
                "weight_kg": FieldValue(value=48.5, unit="kg", confidence=0.87, status="extracted"),
            },
            overall_confidence=0.88,
            review_status="pending"
        )
        record("Full ProductRecord creation", True, f"id={pr.product_id}, fields={len(pr.specifications)}")
    except Exception as e:
        record("Full ProductRecord creation", False, str(e))

    # Test JSON serialization round-trip
    try:
        json_str = pr.model_dump_json()
        pr2 = ProductRecord.model_validate_json(json_str)
        assert pr2.product_id == pr.product_id
        assert pr2.specifications["voltage"].value == "480V"
        record("ProductRecord JSON round-trip", True, f"JSON size={len(json_str)} bytes")
    except Exception as e:
        record("ProductRecord JSON round-trip", False, str(e))

# ────────────────────────────────────────────────────────────────
# 2. INGESTION TESTS
# ────────────────────────────────────────────────────────────────
def test_ingestion():
    section("2. INGESTION & SOURCE REGISTRATION")
    from backend.ingest import register_source, detect_source_type, save_uploaded_file

    # Test type detection
    for fname, expected in [("datasheet.pdf", "pdf"), ("nameplate.jpg", "image"), ("nameplate.png", "image"), ("erp.csv", "csv")]:
        detected = detect_source_type(fname)
        record(f"Detect '{fname}' → {detected}", detected == expected, f"expected={expected}")

    # Test source registration with real CSV test file
    csv_path = str(Path(__file__).parent / "test_data" / "sample_erp_export.csv")
    if Path(csv_path).exists():
        src = register_source(csv_path, "sample_erp_export.csv")
        record("Register CSV source", True, f"source_id={src.source_id}, type={src.source_type}")
        assert src.source_id.startswith("csv_")
        record("Source ID hash prefix", src.source_id.startswith("csv_"), src.source_id)
    else:
        record("Register CSV source", False, f"File not found: {csv_path}")

# ────────────────────────────────────────────────────────────────
# 3. EXTRACTION TESTS (Fallback mode — no API key)
# ────────────────────────────────────────────────────────────────
def test_extraction():
    section("3. MULTIMODAL EXTRACTION (Fallback/Demo Mode)")
    from backend.extract import extract_from_pdf, extract_from_image, extract_from_csv

    # PDF extraction (fallback)
    pdf_fields = extract_from_pdf("fake_datasheet.pdf", "pdf_test123")
    record("PDF fallback extraction returns fields", len(pdf_fields) > 0, f"fields={list(pdf_fields.keys())}")
    
    if "product_name" in pdf_fields:
        pn = pdf_fields["product_name"]
        record("PDF: product_name has value", pn.value is not None, f"value='{pn.value}'")
        record("PDF: product_name has provenance", len(pn.provenance) > 0, f"provenance_count={len(pn.provenance)}")
        record("PDF: provenance has location", pn.provenance[0].location is not None, pn.provenance[0].location)
        record("PDF: provenance has raw_snippet", pn.provenance[0].raw_snippet is not None)

    if "voltage" in pdf_fields:
        v = pdf_fields["voltage"]
        record("PDF: voltage extracted", v.value is not None, f"value='{v.value}', unit='{v.unit}'")

    # Image extraction (fallback)
    img_fields = extract_from_image("fake_nameplate.jpg", "img_test456")
    record("Image fallback extraction returns fields", len(img_fields) > 0, f"fields={list(img_fields.keys())}")

    if "voltage" in img_fields:
        v = img_fields["voltage"]
        record("Image: voltage extracted", v.value is not None, f"value='{v.value}'")
        # This should intentionally differ from PDF (460V vs 480V) for conflict demo
        record("Image: voltage differs from PDF (conflict engineered)", 
               str(img_fields.get("voltage", {}).value) != str(pdf_fields.get("voltage", {}).value),
               f"PDF={pdf_fields.get('voltage', {}).value} vs Image={img_fields.get('voltage', {}).value}")

    # CSV extraction
    csv_path = str(Path(__file__).parent / "test_data" / "sample_erp_export.csv")
    csv_fields = extract_from_csv(csv_path, "csv_test789")
    record("CSV extraction returns fields", len(csv_fields) > 0, f"fields={list(csv_fields.keys())}")
    
    if "product_name" in csv_fields:
        record("CSV: product_name extracted", csv_fields["product_name"].value is not None, f"value='{csv_fields['product_name'].value}'")
        record("CSV: confidence is high (0.95)", csv_fields["product_name"].confidence == 0.95)

    return pdf_fields, img_fields, csv_fields

# ────────────────────────────────────────────────────────────────
# 4. MERGE & CONFLICT RESOLUTION TESTS
# ────────────────────────────────────────────────────────────────
def test_merge(pdf_fields, img_fields, csv_fields):
    section("4. MULTI-SOURCE MERGE & CONFLICT RESOLUTION")
    from backend.merge import merge_field, merge_extractions
    from backend.models import FieldValue, Provenance

    # Test: All sources agree → confidence boost
    candidates_agree = [
        FieldValue(value="VD-X500-480V-3P", confidence=0.90, status="extracted",
                   provenance=[Provenance(source_id="pdf_1", source_type="pdf", extraction_method="test", confidence=0.90)]),
        FieldValue(value="VD-X500-480V-3P", confidence=0.96, status="extracted",
                   provenance=[Provenance(source_id="img_1", source_type="image", extraction_method="test", confidence=0.96)]),
    ]
    merged = merge_field("model_number", candidates_agree)
    record("Merge: sources agree → boosted confidence", merged.confidence > 0.96, f"conf={merged.confidence}")
    record("Merge: sources agree → status='extracted'", merged.status == "extracted")
    record("Merge: provenance combined", len(merged.provenance) == 2, f"prov_count={len(merged.provenance)}")

    # Test: Sources disagree → conflict surfaced
    candidates_conflict = [
        FieldValue(value="480V", confidence=0.85, status="extracted",
                   provenance=[Provenance(source_id="pdf_1", source_type="pdf", extraction_method="test", confidence=0.85)]),
        FieldValue(value="460V", confidence=0.91, status="extracted",
                   provenance=[Provenance(source_id="img_1", source_type="image", extraction_method="test", confidence=0.91)]),
    ]
    merged_conflict = merge_field("voltage", candidates_conflict)
    record("Merge: sources disagree → status='conflicted'", merged_conflict.status == "conflicted")
    record("Merge: conflict → confidence penalized (0.7x)", merged_conflict.confidence < 0.91, f"conf={merged_conflict.confidence}")
    record("Merge: conflict_candidates populated", merged_conflict.conflict_candidates is not None and len(merged_conflict.conflict_candidates) > 0,
           f"candidates={len(merged_conflict.conflict_candidates or [])}")

    # Test: Full multi-source merge
    all_extractions = [pdf_fields, img_fields, csv_fields]
    merged_all = merge_extractions(all_extractions)
    record("Full merge: combined field count", len(merged_all) > 0, f"merged_fields={list(merged_all.keys())}")
    
    # Voltage should be conflicted (480V from PDF vs 460V from image)
    if "voltage" in merged_all:
        record("Full merge: voltage is CONFLICTED", merged_all["voltage"].status == "conflicted", f"status={merged_all['voltage'].status}")

    return merged_all

# ────────────────────────────────────────────────────────────────
# 5. ENRICHMENT TESTS
# ────────────────────────────────────────────────────────────────
def test_enrichment():
    section("5. RAG ENRICHMENT (Seed Knowledge Base)")
    from backend.enrich import enrich_missing_fields, load_seed_documents, EmbeddedRetriever
    from backend.models import ProductRecord, FieldValue

    # Test seed document loading
    docs = load_seed_documents()
    record("Seed KB documents loaded", len(docs) > 0, f"doc_count={len(docs)}")

    # Test retriever queries
    retriever = EmbeddedRetriever()
    matches = retriever.query("Industrial Motors & Drives", "category")
    record("Retriever: category query returns matches", len(matches) > 0, f"match_count={len(matches)}")

    # Test enrichment on a product with missing fields
    record_obj = ProductRecord(
        product_id="ENRICH-TEST-01",
        product_name=FieldValue(value="Test Motor", confidence=0.9, status="extracted"),
        manufacturer=FieldValue(value="Test Corp", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="TM-100", confidence=0.92, status="extracted"),
        category=FieldValue(value="Industrial Motors & Drives", confidence=0.88, status="extracted"),
        description_short=FieldValue(value="Test motor", confidence=0.8),
        description_long=FieldValue(value="A test motor for enrichment testing", confidence=0.8),
        # warranty and certifications intentionally missing
    )

    enriched = enrich_missing_fields(record_obj)
    record("Enrichment: warranty filled from KB", enriched.warranty is not None and enriched.warranty.value is not None,
           f"warranty='{enriched.warranty.value if enriched.warranty else None}'")
    record("Enrichment: warranty provenance is 'rag_enrichment'",
           enriched.warranty is not None and len(enriched.warranty.provenance) > 0 and enriched.warranty.provenance[0].source_type == "rag_enrichment")
    record("Enrichment: certifications filled", len(enriched.certifications) > 0,
           f"certs_count={len(enriched.certifications)}")
    record("Enrichment: accessories filled from taxonomy", len(enriched.accessories) > 0,
           f"accessories={enriched.accessories}")

# ────────────────────────────────────────────────────────────────
# 6. KNOWLEDGE GRAPH TESTS
# ────────────────────────────────────────────────────────────────
def test_knowledge_graph():
    section("6. NETWORKX KNOWLEDGE GRAPH")
    from backend.knowledge_graph import G, add_product_to_graph, find_category_siblings, check_consistency, export_graph_json
    from backend.models import ProductRecord, FieldValue

    initial_nodes = len(G.nodes)
    record("Seed graph pre-populated", initial_nodes > 0, f"nodes={initial_nodes}, edges={len(G.edges)}")

    # Add a new product
    test_product = ProductRecord(
        product_id="KG-TEST-01",
        product_name=FieldValue(value="KG Test Motor", confidence=0.9, status="extracted"),
        manufacturer=FieldValue(value="KG Corp", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="KG-100", confidence=0.92, status="extracted"),
        category=FieldValue(value="Industrial Motors & Drives", confidence=0.88, status="extracted"),
        description_short=FieldValue(value="KG test motor", confidence=0.8),
        description_long=FieldValue(value="A test motor for KG testing", confidence=0.8),
        specifications={
            "weight_kg": FieldValue(value=48.0, unit="kg", confidence=0.89, status="extracted"),
        },
        accessories=["Braking Resistor Module", "Encoder Cable"],
    )
    add_product_to_graph(test_product)
    record("Product added to graph", "KG-TEST-01" in G.nodes, f"total_nodes={len(G.nodes)}")
    record("Category edge created", G.has_edge("KG-TEST-01", "Industrial Motors & Drives"))

    # Test sibling finding
    siblings = find_category_siblings(test_product)
    record("Category siblings found", len(siblings) > 0, f"siblings={siblings}")

    # Test consistency check (normal weight — should pass)
    warnings = check_consistency(test_product)
    record("Consistency check: normal weight → no warnings", len(warnings) == 0, f"warnings={len(warnings)}")

    # Test consistency check with outlier weight
    outlier_product = ProductRecord(
        product_id="KG-OUTLIER-01",
        product_name=FieldValue(value="Outlier Motor", confidence=0.9, status="extracted"),
        manufacturer=FieldValue(value="Outlier Corp", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="OUT-999", confidence=0.92, status="extracted"),
        category=FieldValue(value="Industrial Motors & Drives", confidence=0.88, status="extracted"),
        description_short=FieldValue(value="Outlier test", confidence=0.8),
        description_long=FieldValue(value="Product with abnormal weight", confidence=0.8),
        specifications={
            "weight_kg": FieldValue(value=5000.0, unit="kg", confidence=0.7, status="extracted"),
        },
    )
    add_product_to_graph(outlier_product)
    outlier_warnings = check_consistency(outlier_product)
    record("Consistency check: outlier weight → WARNING flagged", len(outlier_warnings) > 0,
           f"warning='{outlier_warnings[0]['message'][:80]}...'" if outlier_warnings else "no warning")

    # Test graph export for D3
    graph_json = export_graph_json()
    record("Graph export: has nodes", len(graph_json["nodes"]) > 0, f"nodes={len(graph_json['nodes'])}")
    record("Graph export: has links", len(graph_json["links"]) > 0, f"links={len(graph_json['links'])}")

# ────────────────────────────────────────────────────────────────
# 7. VALIDATION TESTS
# ────────────────────────────────────────────────────────────────
def test_validation():
    section("7. BUSINESS RULES VALIDATION & CONFIDENCE SCORING")
    from backend.validate import validate_record, check_voltage_sanity, check_numeric_range
    from backend.models import ProductRecord, FieldValue

    # Unit checks
    record("Voltage sanity: 480V → valid", check_voltage_sanity("480V"))
    record("Voltage sanity: 0V → invalid", not check_voltage_sanity("0V"))
    record("Numeric range: 48.5 in [0.01, 50000] → valid", check_numeric_range(48.5, 0.01, 50000.0))
    record("Numeric range: -5 in [0.01, 50000] → invalid", not check_numeric_range(-5, 0.01, 50000.0))

    # Full record validation
    test_record = ProductRecord(
        product_id="VAL-TEST-01",
        product_name=FieldValue(value="Validated Motor", confidence=0.9, status="extracted"),
        manufacturer=FieldValue(value="Val Corp", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="VM-100", confidence=0.88, status="extracted"),
        category=FieldValue(value="Industrial Motors & Drives", confidence=0.85, status="extracted"),
        description_short=FieldValue(value="Validated test motor", confidence=0.8),
        description_long=FieldValue(value="Motor for validation testing", confidence=0.8),
        specifications={
            "voltage": FieldValue(value="480V", unit="V", confidence=0.9, status="extracted"),
            "weight_kg": FieldValue(value=48.5, unit="kg", confidence=0.87, status="extracted"),
            "power_watts": FieldValue(value="15000W", unit="W", confidence=0.85, status="extracted"),
        },
    )
    validated = validate_record(test_record)
    record("Validation: overall_confidence computed", validated.overall_confidence > 0, f"overall={validated.overall_confidence}")
    record("Validation: review_status set", validated.review_status in ["pending", "needs_review"], f"status={validated.review_status}")

    # Test with invalid spec (negative weight)
    bad_record = ProductRecord(
        product_id="VAL-BAD-01",
        product_name=FieldValue(value="Bad Product", confidence=0.5, status="extracted"),
        manufacturer=FieldValue(value="Bad Corp", confidence=0.5, status="extracted"),
        model_number=FieldValue(value="BAD-1", confidence=0.5, status="extracted"),
        category=FieldValue(value="Test", confidence=0.5, status="extracted"),
        description_short=FieldValue(value="Bad product", confidence=0.3),
        description_long=FieldValue(value="Product with bad specs", confidence=0.3),
        specifications={
            "weight_kg": FieldValue(value=-10.0, unit="kg", confidence=0.8, status="extracted"),
        },
    )
    validated_bad = validate_record(bad_record)
    record("Validation: invalid weight → needs_review", validated_bad.specifications["weight_kg"].status == "needs_review")
    record("Validation: invalid weight → confidence halved", validated_bad.specifications["weight_kg"].confidence < 0.8,
           f"conf={validated_bad.specifications['weight_kg'].confidence}")

# ────────────────────────────────────────────────────────────────
# 8. DATABASE TESTS
# ────────────────────────────────────────────────────────────────
async def test_database():
    section("8. SQLITE DATABASE PERSISTENCE")
    from backend.database import init_db, save_product, get_product, list_products, save_source, get_source, log_edit, get_product_edits, DB_PATH
    from backend.models import ProductRecord, FieldValue, SourceDocument

    # Ensure clean state for test
    if DB_PATH.exists():
        DB_PATH.unlink()

    await init_db()
    record("Database initialized", DB_PATH.exists(), f"path={DB_PATH}")

    # Save and retrieve source
    src = SourceDocument(source_id="test_src_001", source_type="pdf", file_path="/test/file.pdf", filename="file.pdf")
    await save_source(src)
    retrieved_src = await get_source("test_src_001")
    record("Source save & retrieve", retrieved_src is not None and retrieved_src.source_id == "test_src_001")

    # Save and retrieve product
    prod = ProductRecord(
        product_id="DB-TEST-01",
        product_name=FieldValue(value="DB Test Product", confidence=0.92, status="extracted"),
        manufacturer=FieldValue(value="DB Corp", confidence=0.95, status="extracted"),
        model_number=FieldValue(value="DB-100", confidence=0.88, status="extracted"),
        category=FieldValue(value="Test Category", confidence=0.85, status="extracted"),
        description_short=FieldValue(value="DB test product", confidence=0.8),
        description_long=FieldValue(value="A database test product", confidence=0.8),
        specifications={"voltage": FieldValue(value="240V", unit="V", confidence=0.9, status="extracted")},
        overall_confidence=0.88,
        review_status="pending",
    )
    await save_product(prod)
    retrieved = await get_product("DB-TEST-01")
    record("Product save & retrieve", retrieved is not None and retrieved.product_id == "DB-TEST-01")
    record("Product specs preserved", "voltage" in retrieved.specifications, f"voltage={retrieved.specifications.get('voltage', {}).value if retrieved else 'N/A'}")

    # List products
    products = await list_products()
    record("List products", len(products) > 0, f"count={len(products)}")

    # Log and retrieve edits
    await log_edit("DB-TEST-01", "voltage", "240V", "480V", "test_reviewer", datetime.utcnow().isoformat(), "test correction")
    edits = await get_product_edits("DB-TEST-01")
    record("Edit log save & retrieve", len(edits) > 0, f"edits_count={len(edits)}")
    record("Edit log content correct", edits[0]["old_value"] == '"240V"' or edits[0]["old_value"] == "240V")

# ────────────────────────────────────────────────────────────────
# 9. PIPELINE INTEGRATION TEST
# ────────────────────────────────────────────────────────────────
async def test_pipeline():
    section("9. END-TO-END PIPELINE INTEGRATION")
    from backend.pipeline import run_product_intelligence_pipeline
    from backend.database import init_db, get_product

    await init_db()

    # Run full pipeline with demo sources
    product = await run_product_intelligence_pipeline(
        source_ids=["pdf_demo", "image_demo", "csv_demo"],
        product_id="E2E-TEST-001"
    )

    record("Pipeline: product created", product is not None)
    record("Pipeline: product_id correct", product.product_id == "E2E-TEST-001")
    record("Pipeline: product_name populated", product.product_name.value is not None, f"name='{product.product_name.value}'")
    record("Pipeline: manufacturer populated", product.manufacturer.value is not None, f"mfr='{product.manufacturer.value}'")
    record("Pipeline: model_number populated", product.model_number.value is not None, f"model='{product.model_number.value}'")
    record("Pipeline: category populated", product.category.value is not None, f"cat='{product.category.value}'")
    record("Pipeline: specifications count", len(product.specifications) > 0, f"spec_count={len(product.specifications)}")
    record("Pipeline: overall_confidence computed", product.overall_confidence > 0, f"conf={product.overall_confidence}")
    record("Pipeline: review_status set", product.review_status in ["pending", "needs_review", "approved"], f"status={product.review_status}")

    # Check voltage conflict was detected (480V from PDF vs 460V from image)
    if "voltage" in product.specifications:
        v = product.specifications["voltage"]
        record("Pipeline: voltage field exists", True, f"value={v.value}, status={v.status}")
        record("Pipeline: voltage is CONFLICTED (460V vs 480V)", v.status == "conflicted", f"status={v.status}")
        if v.conflict_candidates:
            record("Pipeline: conflict candidates surfaced", len(v.conflict_candidates) >= 2,
                   f"candidates={[c.get('value') for c in v.conflict_candidates]}")

    # Unilog Industrial Commerce Features Verification
    record("Pipeline: UNSPSC code assigned", product.unspsc_code is not None and product.unspsc_code.value is not None, f"unspsc='{product.unspsc_code.value if product.unspsc_code else None}'")
    record("Pipeline: ETIM class assigned", product.etim_class is not None and product.etim_class.value is not None, f"etim='{product.etim_class.value if product.etim_class else None}'")
    record("Pipeline: CRI score computed", product.commerce_readiness_score > 0, f"CRI={product.commerce_readiness_score}%")
    record("Pipeline: SEO title synthesized", product.seo_title is not None and product.seo_title.value is not None, f"seo='{product.seo_title.value if product.seo_title else None}'")
    record("Pipeline: Interchangeable parts matched", len(product.interchangeable_parts) > 0, f"matches={len(product.interchangeable_parts)}")

    # Verify persisted to database
    db_product = await get_product("E2E-TEST-001")
    record("Pipeline: product persisted to SQLite", db_product is not None)

    return product

# ────────────────────────────────────────────────────────────────
# 10. HUMAN REVIEW TESTS
# ────────────────────────────────────────────────────────────────
async def test_human_review(product):
    section("10. HUMAN-IN-THE-LOOP REVIEW & AUDIT TRAIL")
    from backend.human_review import log_human_edit, approve_record
    from backend.database import init_db, get_product, get_product_edits

    await init_db()

    # Edit a field
    updated = await log_human_edit(
        record=product,
        field_name="voltage",
        new_value="480V",
        unit="V",
        reviewer="judge_reviewer",
        reason="Confirmed correct voltage from physical inspection"
    )
    record("Human edit: field updated", True)
    
    if "voltage" in updated.specifications:
        v = updated.specifications["voltage"]
        record("Human edit: voltage set to 480V", str(v.value) == "480V", f"value={v.value}")
        record("Human edit: status → human_verified", v.status == "human_verified")
        record("Human edit: confidence → 1.0", v.confidence == 1.0, f"conf={v.confidence}")
        record("Human edit: provenance trail extended", len(v.provenance) > 1, f"prov_count={len(v.provenance)}")

    # Check audit log
    record("Human edit: log entry added", len(updated.human_edits_log) > 0, f"log_count={len(updated.human_edits_log)}")

    # Approve record
    approved = await approve_record(product.product_id, reviewer="judge_reviewer")
    record("Approve: record approved", approved is not None and approved.review_status == "approved", f"status={approved.review_status if approved else 'None'}")

    # Verify audit trail in database
    edits = await get_product_edits(product.product_id)
    record("Audit trail: edits persisted in DB", len(edits) > 0, f"db_edits={len(edits)}")


# ────────────────────────────────────────────────────────────────
# MAIN RUNNER
# ────────────────────────────────────────────────────────────────
async def main():
    print("\n" + "#"*60)
    print("  SPECTRA AI -- FULL E2E TEST SUITE")
    print("  " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("#"*60)

    test_data_models()
    test_ingestion()
    pdf_f, img_f, csv_f = test_extraction()
    test_merge(pdf_f, img_f, csv_f)
    test_enrichment()
    test_knowledge_graph()
    test_validation()
    await test_database()
    product = await test_pipeline()
    await test_human_review(product)

    # ── Summary ──
    section("FINAL TEST REPORT SUMMARY")
    total = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    failed = sum(1 for r in results if r["status"] == FAIL)
    
    print(f"\n  Total Tests:  {total}")
    print(f"  Passed:       {passed}  ({passed/total*100:.0f}%)")
    print(f"  Failed:       {failed}  ({failed/total*100:.0f}%)")
    print(f"\n{'='*60}")

    if failed > 0:
        print("\n  FAILED TESTS:")
        for r in results:
            if r["status"] == FAIL:
                print(f"    {FAIL}  {r['test']}  ({r['detail']})")
    else:
        print(f"\n  >>> ALL {total} TESTS PASSED! <<<")

    print(f"\n{'='*60}\n")

    # Write structured JSON report
    report_path = Path(__file__).parent / "test_report.json"
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed/total*100:.1f}%",
        "results": results,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
    print(f"  JSON report saved to: {report_path}\n")

    return report

if __name__ == "__main__":
    report = asyncio.run(main())
