"""FastAPI application: URL shortener service."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import URL

from database import close_db, get_session, init_db
from models import (
    URLRecord,
    EncurtarRequest,
    EncurtarResponse,
    URLStatsResponse,
    HealthResponse,
    MAX_COLLISION_RETRIES,
)
# Import the models module for testability (allows monkeypatching generate_short_code)
import models as _models_module


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="URL Shortener",
    description="Encurtador de URLs — API Bitly-like simplificada",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Helpers ──────────────────────────────────────────────────────────
def _build_short_url(request: Request, short_code: str) -> str:
    """Build the absolute short URL from the incoming request's base URL."""
    base: URL = request.base_url
    # Remove trailing slash so /abc123 doesn't double-slash
    return str(base).rstrip("/") + f"/{short_code}"


async def _find_by_short_code(
    session: AsyncSession, short_code: str
) -> URLRecord | None:
    """Look up a URL record by its short code."""
    result = await session.execute(
        select(URLRecord).where(URLRecord.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def _find_by_original_url(
    session: AsyncSession, original_url: str
) -> URLRecord | None:
    """Look up a URL record by the original (long) URL."""
    result = await session.execute(
        select(URLRecord).where(URLRecord.original_url == original_url)
    )
    return result.scalar_one_or_none()


async def _create_short_url(session: AsyncSession, original_url: str) -> URLRecord:
    """Generate a unique short code and persist the record."""
    for attempt in range(1, MAX_COLLISION_RETRIES + 1):
        code = _models_module.generate_short_code()
        existing = await _find_by_short_code(session, code)
        if existing is None:
            record = URLRecord(short_code=code, original_url=original_url)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record
    raise RuntimeError(
        f"Não foi possível gerar um short_code único após "
        f"{MAX_COLLISION_RETRIES} tentativas"
    )


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health-check endpoint."""
    return HealthResponse()


@app.post(
    "/encurtar",
    response_model=EncurtarResponse,
    status_code=status.HTTP_201_CREATED,
)
async def encurtar(request: Request, body: EncurtarRequest):
    """
    Encurta uma URL longa.

    Se a URL já foi encurtada antes, retorna o mesmo short_code.
    """
    async with get_session() as session:  # type: AsyncSession

        # ── Deduplicação: mesma URL → mesmo short_code ──
        existing = await _find_by_original_url(session, body.url)
        if existing is not None:
            return EncurtarResponse(
                short_code=existing.short_code,
                short_url=_build_short_url(request, existing.short_code),
                original_url=existing.original_url,
            )

        # ── Geração com retry ──
        record = await _create_short_url(session, body.url)

    return EncurtarResponse(
        short_code=record.short_code,
        short_url=_build_short_url(request, record.short_code),
        original_url=record.original_url,
    )


@app.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
)
async def get_stats(short_code: str):
    """Retorna estatísticas de um short_code (sem incrementar clicks)."""
    async with get_session() as session:  # type: AsyncSession
        record = await _find_by_short_code(session, short_code)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short code não encontrado",
            )
        return URLStatsResponse(
            short_code=record.short_code,
            short_url=record.short_code,  # relative, caller adds base
            original_url=record.original_url,
            clicks=record.clicks,
            created_at=record.created_at.isoformat() if record.created_at else "",
        )


@app.get("/{short_code}")
async def redirect(short_code: str):
    """
    Redireciona para a URL original via HTTP 302.

    Incrementa o contador de clicks a cada acesso.
    Retorna 404 se o short_code não existir.
    """
    async with get_session() as session:  # type: AsyncSession
        record = await _find_by_short_code(session, short_code)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short code não encontrado",
            )

        # ── Incrementa clicks (atômico no banco) ──
        record.clicks += 1
        await session.commit()

    return RedirectResponse(
        url=record.original_url,
        status_code=status.HTTP_302_FOUND,
    )
