from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class CatalogItem(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    url: HttpUrl
    description: str = ""
    duration: str = ""
    test_type: str = Field(default="Unknown", min_length=1)
    keywords: list[str] = Field(default_factory=list)
    category: str = ""
    job_levels: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    remote_testing: bool = True

    @field_validator("keywords", "job_levels", "languages", mode="before")
    @classmethod
    def normalize_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
        if isinstance(value, list):
            return [str(part).strip() for part in value if str(part).strip()]
        return []

    @property
    def search_text(self) -> str:
        pieces = [
            self.name,
            self.description,
            self.duration,
            self.test_type,
            self.category,
            " ".join(self.keywords),
            " ".join(self.job_levels),
            " ".join(self.languages),
            "remote testing" if self.remote_testing else "",
        ]
        return " | ".join(piece for piece in pieces if piece)

