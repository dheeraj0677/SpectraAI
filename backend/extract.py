import os
import re
import csv
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import anthropic
from pypdf import PdfReader
from backend.models import FieldValue, Provenance
from backend.normalize import normalize_field_value, canonicalize_field_name

logger = logging.getLogger("extract")

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field_name": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": ["string", "null"]},
                    "confidence": {"type": "number"},
                    "location": {"type": "string"},
                    "raw_snippet": {"type": "string"}
                },
                "required": ["field_name", "value", "confidence", "location"]
            }
        }
    },
    "required": ["fields"]
}

EXTRACTION_PROMPT = """
You are extracting structured product data from a manufacturer document.

Extract every identifiable product attribute you can find:
- product_name, manufacturer, model_number, sku, category
- description_short, description_long
- dimensions, weight_kg, voltage, power_watts, max_current_amps, operating_temp
- certifications, warranty, country_of_origin
- compatible_with, replaces, accessories

For EACH field you extract:
- Give the exact value and unit if applicable
- Cite the LOCATION you found it (page number + table/section, or approximate position on nameplate/spec sheet)
- Give a confidence score 0.0-1.0 based on how explicit/unambiguous the source text is
- Include a short raw snippet (<20 words) as evidence

Do NOT infer or guess values that are not explicitly stated in this document.
If a field is ambiguous or the document conflicts with itself, extract both
candidate values and lower the confidence score accordingly.
"""

def get_anthropic_client() -> Optional[anthropic.Anthropic]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    return None

def extract_from_pdf_pypdf(pdf_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Real offline text extraction and spec parsing from PDF documents using pypdf."""
    results = {}
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        page_texts = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            page_texts.append((i + 1, text))
            full_text += f"\n--- Page {i+1} ---\n" + text

        if len(full_text.strip()) < 20:
            return results

        # Heuristic extraction patterns for standard technical spec lines
        patterns = [
            ("product_name", r"(?:product\s*name|datasheet|item)[\s:]+([^\n\r]+)", "Page 1, Header"),
            ("manufacturer", r"(?:manufacturer|brand|mfr|company)[\s:]+([^\n\r]+)", "Page 1, Header"),
            ("model_number", r"(?:model|model\s*number|model\s*no\.?|mpn)[\s:]+([^\n\r]+)", "Page 1, Specifications"),
            ("category", r"(?:category|type|product\s*family)[\s:]+([^\n\r]+)", "Page 1, Classification"),
            ("voltage", r"(?:voltage|rated\s*voltage|operating\s*voltage)[\s:]+([^\n\r]+)", "Electrical Specs"),
            ("power_watts", r"(?:power|power\s*rating|rated\s*power)[\s:]+([^\n\r]+)", "Electrical Specs"),
            ("weight_kg", r"(?:weight|net\s*weight|mass)[\s:]+([^\n\r]+)", "Physical Specs"),
            ("certifications", r"(?:certifications|compliance|standards)[\s:]+([^\n\r]+)", "Compliance Section"),
            ("description_long", r"(?:description|overview)[\s:]+([^\n\r]+)", "Overview"),
        ]

        for fname, pattern, default_loc in patterns:
            for page_num, text in page_texts:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    val_str = match.group(1).strip()
                    if val_str and fname not in results:
                        prov = Provenance(
                            source_id=source_id,
                            source_type="pdf",
                            location=f"Page {page_num}, {default_loc}",
                            extraction_method="pypdf-text-extraction",
                            confidence=0.92,
                            raw_snippet=f"{match.group(0)[:60]}...",
                            is_synthetic=False,
                            observation_type="directly_observed"
                        )
                        fv = FieldValue(
                            value=val_str,
                            confidence=0.92,
                            provenance=[prov],
                            status="extracted",
                            is_synthetic=False,
                            observation_type="directly_observed"
                        )
                        results[fname] = normalize_field_value(fname, fv)
                        break

    except Exception as e:
        logger.warning(f"pypdf extraction failed for {pdf_path}: {e}")

    return results

def extract_from_pdf(pdf_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Extract structured specs from PDF using Claude Vision, pypdf text parser, or demo fallback."""
    client = get_anthropic_client()
    file_path = Path(pdf_path)

    # 1. If Claude API client is configured, use multimodal vision
    if client:
        try:
            pdf_bytes = file_path.read_bytes()
            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                output_config={"format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_b64
                            }
                        },
                        {"type": "text", "text": EXTRACTION_PROMPT}
                    ]
                }]
            )

            raw_text = response.content[0].text
            data = json.loads(raw_text)
            return parse_extracted_fields(data.get("fields", []), source_id, source_type="pdf", method="claude-vision-extraction", is_synthetic=False)
        except Exception as e:
            logger.error(f"Error calling Claude for PDF {file_path.name}: {e}. Trying offline text extraction...")

    # 2. Try offline real text parsing via pypdf
    if file_path.exists():
        real_extracted = extract_from_pdf_pypdf(str(file_path), source_id)
        if len(real_extracted) >= 3:
            logger.info(f"Successfully extracted {len(real_extracted)} fields from real PDF via pypdf.")
            return real_extracted

    # 3. Fallback to synthetic demo data
    logger.info(f"Using synthetic demo fallback for PDF {file_path.name}")
    return fallback_pdf_extraction(pdf_path, source_id)

def extract_from_image(image_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Extract structured specs from Image using Claude Vision or demo fallback."""
    client = get_anthropic_client()
    file_path = Path(image_path)

    if client:
        try:
            image_bytes = file_path.read_bytes()
            ext = file_path.suffix.lower().replace(".", "")
            media_type = f"image/{ext}" if ext in ["png", "jpeg", "webp", "gif"] else "image/jpeg"
            img_b64 = base64.b64encode(image_bytes).decode("utf-8")

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                output_config={"format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": img_b64
                            }
                        },
                        {"type": "text", "text": EXTRACTION_PROMPT}
                    ]
                }]
            )

            raw_text = response.content[0].text
            data = json.loads(raw_text)
            return parse_extracted_fields(data.get("fields", []), source_id, source_type="image", method="claude-vision-extraction", is_synthetic=False)
        except Exception as e:
            logger.error(f"Error calling Claude for Image {file_path.name}: {e}. Falling back...")

    return fallback_image_extraction(image_path, source_id)

def extract_from_csv(csv_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Extract structured fields directly from CSV records."""
    results = {}
    file_path = Path(csv_path)
    if not file_path.exists():
        return results

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if row:
                row_idx = 1
                for key, raw_val in row.items():
                    if not raw_val or not raw_val.strip():
                        continue
                    clean_key = canonicalize_field_name(key)
                    val_str = raw_val.strip()

                    prov = Provenance(
                        source_id=source_id,
                        source_type="csv",
                        location=f"CSV row {row_idx}, column '{key}'",
                        extraction_method="csv-direct",
                        confidence=0.95,
                        raw_snippet=f"{key}: {val_str}",
                        is_synthetic=False,
                        observation_type="directly_observed"
                    )

                    raw_fv = FieldValue(
                        value=val_str,
                        unit=None,
                        confidence=0.95,
                        provenance=[prov],
                        status="extracted",
                        is_synthetic=False,
                        observation_type="directly_observed"
                    )
                    results[clean_key] = normalize_field_value(clean_key, raw_fv)
    except Exception as e:
        logger.error(f"Failed to extract CSV {csv_path}: {e}")

    return results

def parse_extracted_fields(
    fields: List[Dict[str, Any]],
    source_id: str,
    source_type: str,
    method: str,
    is_synthetic: bool = False
) -> Dict[str, FieldValue]:
    results = {}
    for f in fields:
        fname = canonicalize_field_name(f.get("field_name", ""))
        if not fname:
            continue
        val = f.get("value")
        unit = f.get("unit")
        conf = float(f.get("confidence", 0.8))
        loc = f.get("location", "document body")
        snip = f.get("raw_snippet", str(val))

        prov = Provenance(
            source_id=source_id,
            source_type=source_type,  # type: ignore
            location=loc,
            extraction_method=method,
            confidence=conf,
            raw_snippet=snip,
            is_synthetic=is_synthetic,
            observation_type="heuristically_inferred" if is_synthetic else "directly_observed"
        )

        raw_fv = FieldValue(
            value=val,
            unit=unit,
            confidence=conf,
            provenance=[prov],
            status="extracted",
            is_synthetic=is_synthetic,
            observation_type="heuristically_inferred" if is_synthetic else "directly_observed"
        )
        results[fname] = normalize_field_value(fname, raw_fv)
    return results

def fallback_pdf_extraction(pdf_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Explicit synthetic fallback when API key is absent and pypdf has insufficient text."""
    results = {}

    def make_synthetic(field: str, val: Any, unit: Optional[str], conf: float, loc: str, snip: str):
        prov = Provenance(
            source_id=source_id,
            source_type="synthetic_demo",
            location=loc,
            extraction_method="synthetic-fallback-demo",
            confidence=conf,
            raw_snippet=f"[Synthetic Fixture] {snip}",
            is_synthetic=True,
            observation_type="heuristically_inferred"
        )
        fv = FieldValue(
            value=val,
            unit=unit,
            confidence=conf,
            status="extracted",
            provenance=[prov],
            is_synthetic=True,
            observation_type="heuristically_inferred"
        )
        return normalize_field_value(field, fv)

    results["product_name"] = make_synthetic("product_name", "UltraDrive X500 Industrial Inverter Motor", None, 0.92, "Page 1, Header", "UltraDrive X500 Industrial Variable Speed Drive Motor")
    results["manufacturer"] = make_synthetic("manufacturer", "Vortex Dynamics Tech", None, 0.95, "Page 1, Title Block", "Vortex Dynamics Tech Corp")
    results["model_number"] = make_synthetic("model_number", "VD-X500-480V-3P", None, 0.90, "Page 2, Spec Sheet", "Model: VD-X500-480V-3P")
    results["category"] = make_synthetic("category", "Industrial Motors & Drives", None, 0.88, "Page 1, Taxonomy", "Category: Heavy Industrial Electric Motors")
    results["weight_kg"] = make_synthetic("weight_kg", 48.5, "kg", 0.89, "Page 12, Physical Specs Table", "Net Weight: 48.5 kg (106.9 lbs)")
    results["voltage"] = make_synthetic("voltage", "480V", "V", 0.85, "Page 3, Electrical Characteristics", "Rated Voltage: 480V AC 3-Phase 60Hz")
    results["description_long"] = make_synthetic("description_long", "The UltraDrive X500 is a high-performance 480V 3-Phase variable frequency drive designed for heavy industrial automation.", None, 0.90, "Page 1, Overview", "High-performance VFD motor for industrial applications.")
    results["certifications"] = make_synthetic("certifications", "CE, UL 508C, RoHS compliant, IP65 rated", None, 0.94, "Page 14, Standards & Compliance", "Certified UL 508C, CE marking, IP65 enclosure.")

    return results

def fallback_image_extraction(image_path: str, source_id: str) -> Dict[str, FieldValue]:
    """Explicit synthetic fallback for motor nameplate image demo (engineered conflict on voltage)."""
    results = {}

    def make_synthetic(field: str, val: Any, unit: Optional[str], conf: float, loc: str, snip: str):
        prov = Provenance(
            source_id=source_id,
            source_type="synthetic_demo",
            location=loc,
            extraction_method="synthetic-fallback-demo",
            confidence=conf,
            raw_snippet=f"[Synthetic Fixture] {snip}",
            is_synthetic=True,
            observation_type="heuristically_inferred"
        )
        fv = FieldValue(
            value=val,
            unit=unit,
            confidence=conf,
            status="extracted",
            provenance=[prov],
            is_synthetic=True,
            observation_type="heuristically_inferred"
        )
        return normalize_field_value(field, fv)

    results["model_number"] = make_synthetic("model_number", "VD-X500-480V-3P", None, 0.96, "Nameplate photo top line", "MODEL: VD-X500-480V-3P")
    # Engineered conflict: 460V vs 480V in PDF
    results["voltage"] = make_synthetic("voltage", "460V", "V", 0.91, "Nameplate electrical spec block", "VOLTS: 460V 3PH")
    results["power_watts"] = make_synthetic("power_watts", "15000W", "W", 0.93, "Nameplate rating box", "RATING: 15 kW / 20 HP")
    results["sku"] = make_synthetic("sku", "SKU-VDX500-IND", None, 0.88, "Nameplate barcode text", "SKU-VDX500-IND")

    return results
