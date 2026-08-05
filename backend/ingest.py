import hashlib
import shutil
from pathlib import Path
from typing import Literal
from models import SourceDocument

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def detect_source_type(filename: str) -> Literal["pdf", "image", "csv"]:
    ext = Path(filename).suffix.lower()
    if ext in [".pdf"]:
        return "pdf"
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        return "image"
    elif ext in [".csv"]:
        return "csv"
    else:
        # Default to image if unknown image-like or pdf
        return "image"

def register_source(file_path: str, filename: str) -> SourceDocument:
    path_obj = Path(file_path)
    content_bytes = path_obj.read_bytes()
    content_hash = hashlib.sha256(content_bytes).hexdigest()[:12]
    source_type = detect_source_type(filename)
    source_id = f"{source_type}_{content_hash}"
    
    return SourceDocument(
        source_id=source_id,
        source_type=source_type,
        file_path=file_path,
        filename=filename
    )

def save_uploaded_file(file_content: bytes, filename: str) -> SourceDocument:
    dest_path = UPLOAD_DIR / filename
    dest_path.write_bytes(file_content)
    return register_source(str(dest_path), filename)
