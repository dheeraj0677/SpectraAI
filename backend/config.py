import os
from typing import List, Set
from pydantic import BaseModel, Field

class Settings(BaseModel):
    app_name: str = "SpectraAI"
    app_version: str = "1.0.0"
    app_description: str = (
        "SpectraAI — Multimodal product intelligence with source-cited extraction, "
        "RAG enrichment, knowledge graph reasoning, and human-in-the-loop audit trail."
    )
    
    # Server host & port
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    
    # Startup pre-seeding control
    preseed_demo_data: bool = Field(
        default_factory=lambda: os.getenv("PRESEED_DEMO_DATA", "true").lower() in ("true", "1", "yes")
    )
    
    # CORS allowed origins
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ]
    )
    
    # Upload limits (bytes)
    max_upload_size_bytes: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024)))  # 50 MB
    )
    
    # Allowed file extensions for multimodal extraction
    allowed_extensions: Set[str] = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tiff",
        ".csv"
    }
    
    # Allowed MIME types
    allowed_mime_types: Set[str] = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp",
        "image/tiff",
        "text/csv",
        "application/csv",
        "text/plain",
        "application/vnd.ms-excel",
        "application/octet-stream"
    }

    @property
    def has_anthropic_key(self) -> bool:
        """Check if an Anthropic API key is configured without exposing or logging it."""
        return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())

settings = Settings()
