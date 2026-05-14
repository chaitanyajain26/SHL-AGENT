from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SHL Conversational Assessment Recommender"
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    model_name: str = Field(default="llama-3.3-70b-versatile", alias="MODEL_NAME")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    allow_model_download: bool = Field(default=False, alias="ALLOW_MODEL_DOWNLOAD")
    catalog_url: str = Field(default="https://www.shl.com/products/product-catalog/", alias="SHL_CATALOG_URL")
    request_timeout_seconds: int = 20
    max_recommendations: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def root_dir(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def catalog_path(self) -> Path:
        return self.data_dir / "catalog.json"

    @property
    def faiss_dir(self) -> Path:
        return self.data_dir / "faiss_index"


@lru_cache
def get_settings() -> Settings:
    return Settings()
