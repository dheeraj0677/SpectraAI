import pytest
from pathlib import Path
from backend.ingest import detect_source_type, validate_upload, register_source, save_uploaded_file

@pytest.mark.unit
def test_detect_source_type():
    assert detect_source_type("datasheet.pdf") == "pdf"
    assert detect_source_type("nameplate.png") == "image"
    assert detect_source_type("nameplate.jpg") == "image"
    assert detect_source_type("nameplate.jpeg") == "image"
    assert detect_source_type("catalog.csv") == "csv"
    assert detect_source_type("unknown_blob.xyz") == "image"

@pytest.mark.unit
def test_validate_upload_valid():
    validate_upload(b"some content", "datasheet.pdf")
    validate_upload(b"csv,data", "catalog.csv")

@pytest.mark.unit
def test_validate_upload_empty_filename():
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        validate_upload(b"some content", "")

@pytest.mark.unit
def test_validate_upload_empty_content():
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        validate_upload(b"", "datasheet.pdf")

@pytest.mark.unit
def test_validate_upload_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        validate_upload(b"executable", "malware.exe")

@pytest.mark.unit
def test_save_uploaded_file_creates_hashed_file():
    doc = save_uploaded_file(b"test pdf content", "sample_test.pdf")
    assert doc.source_id.startswith("pdf_")
    assert doc.filename == "sample_test.pdf"
    assert Path(doc.file_path).exists()
