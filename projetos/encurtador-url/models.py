"""SQLAlchemy model and Pydantic schemas for URL records."""

from __future__ import annotations

import secrets
import time
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator
from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

# ── Character set without ambiguous characters ──────────────────────
# Excluding: O (capital o), 0 (zero), I (capital i), 1 (one), l (lower L)
SHORT_CODE_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SHORT_CODE_LENGTH = 6
MAX_COLLISION_RETRIES = 10


# ── SQLAlchemy model ────────────────────────────────────────────────
class URLRecord(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(
        String(SHORT_CODE_LENGTH), unique=True, index=True, nullable=False
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<URLRecord short_code={self.short_code!r}>"


# ── Pydantic schemas ────────────────────────────────────────────────
class EncurtarRequest(BaseModel):
    """Request body for POST /encurtar."""

    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("URL não pode estar vazia")
        if not (stripped.startswith("http://") or stripped.startswith("https://")):
            raise ValueError(
                "URL deve começar com http:// ou https://"
            )
        return stripped


class EncurtarResponse(BaseModel):
    """Response body for POST /encurtar."""

    short_code: str
    short_url: str
    original_url: str


class URLStatsResponse(BaseModel):
    """Response body for GET /stats/{short_code}."""

    short_code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: str


class HealthResponse(BaseModel):
    """Response body for GET /."""

    status: str = "ok"


# ── Short-code generation ───────────────────────────────────────────
def generate_short_code() -> str:
    """Generate a random 6-character short code from the safe alphabet."""
    return "".join(secrets.choice(SHORT_CODE_ALPHABET) for _ in range(SHORT_CODE_LENGTH))
