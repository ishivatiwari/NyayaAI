"""
Application configuration via environment variables.
"""
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "nyayaai-dev-secret-change-in-production"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./nyayaai.db"

    # LLM Provider
    LLM_PROVIDER: str = "gemini"  # gemini | openai | azure
    LLM_MODEL: str = "gemini-3.6-flash"

    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None

    # OpenAI (fallback)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # Embeddings
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768

    # Vector Store (ChromaDB)
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "nyayaai_documents"

    # Document Processing
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    MAX_CHUNKS_PER_QUERY: int = 8

    # Storage
    UPLOAD_DIR: str = "./uploads"

    # Demo mode (works without real API key)
    DEMO_MODE: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
