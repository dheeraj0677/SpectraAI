import hashlib
import shutil
from pathlib import Path
from typing import Literal, Optional
from backend.models import SourceDocument
from backend.config import settings

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def detect_source_type(filename: str) -> Literal["pdf", "image", "csv"]:
    """Detect modality source type from file extension."""
    ext = Path(filename).suffix.lower()
    if ext in [".pdf"]:
        return "pdf"
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        return "image"
    elif ext in [".csv"]:
        return "csv"
    else:
        return "image"

def validate_upload(file_content: bytes, filename: str, content_type: Optional[str] = None):
    """Validate upload size, non-emptiness, filename, and extension."""
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")

    sanitized_name = Path(filename).name
    if not sanitized_name:
        raise ValueError("Invalid filename provided")

    ext = Path(sanitized_name).suffix.lower()
    if not ext or ext not in settings.allowed_extensions:
        raise ValueError(
            f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(settings.allowed_extensions))}"
        )

    if len(file_content) == 0:
        raise ValueError("Uploaded file is empty (0 bytes)")

    if len(file_content) > settings.max_upload_size_bytes:
        raise ValueError(
            f"File size ({len(file_content)} bytes) exceeds maximum limit of {settings.max_upload_size_bytes} bytes"
        )

def register_source(file_path: str, filename: str) -> SourceDocument:
    """Register source document with cryptographic SHA-256 ID."""
    path_obj = Path(file_path)
    content_bytes = path_obj.read_bytes()
    content_hash = hashlib.sha256(content_bytes).hexdigest()[:12]
    sanitized_name = Path(filename).name
    source_type = detect_source_type(sanitized_name)
    source_id = f"{source_type}_{content_hash}"

    return SourceDocument(
        source_id=source_id,
        source_type=source_type,
        file_path=file_path,
        filename=sanitized_name
    )

def save_uploaded_file(file_content: bytes, filename: str, content_type: Optional[str] = None) -> SourceDocument:
    """Validate, persist, and register an uploaded source document safely."""
    validate_upload(file_content, filename, content_type)

    sanitized_name = Path(filename).name
    content_hash = hashlib.sha256(file_content).hexdigest()[:12]
    source_type = detect_source_type(sanitized_name)
    source_id = f"{source_type}_{content_hash}"

    # Store with hash prefix to prevent filesystem collisions and directory traversal
    dest_path = UPLOAD_DIR / f"{source_id}_{sanitized_name}"
    dest_path.write_bytes(file_content)

    return SourceDocument(
        source_id=source_id,
        source_type=source_type,
        file_path=str(dest_path),
        filename=sanitized_name
    )
