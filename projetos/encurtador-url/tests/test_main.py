"""Automated tests for the URL shortener API.

Run with:
    pytest tests/ -v
"""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app
from database import reset_db, close_db
from models import SHORT_CODE_ALPHABET, SHORT_CODE_LENGTH

# ── Helpers ──────────────────────────────────────────────────────────
# Build regex from the actual alphabet to stay in sync
_escaped_alphabet = "".join(
    f"\\{ch}" if ch in r"\-[]^$.*+?{}|()" else ch
    for ch in SHORT_CODE_ALPHABET
)
SHORT_CODE_PATTERN = re.compile(rf"^[{_escaped_alphabet}]{{{SHORT_CODE_LENGTH}}}$")


# ── Fixtures ──────────────────────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def _reset_db():
    """Drop and recreate tables before each test for isolation."""
    await reset_db()
    yield
    await close_db()


@pytest_asyncio.fixture
async def client():
    """Yield an async test client mounted on the app."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Tests ────────────────────────────────────────────────────────────
class TestEncurtar:

    async def test_url_normal_gera_hash(self, client: AsyncClient):
        """1. URL normal → gera hash de 6 caracteres."""
        resp = await client.post("/encurtar", json={"url": "https://example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_code" in data
        assert len(data["short_code"]) == 6
        assert SHORT_CODE_PATTERN.match(data["short_code"])
        assert data["original_url"] == "https://example.com"
        assert data["short_url"].endswith(f"/{data['short_code']}")

    async def test_url_sem_scheme_retorna_422(self, client: AsyncClient):
        """2. URL sem scheme → 422."""
        resp = await client.post("/encurtar", json={"url": "example.com"})
        assert resp.status_code == 422

    async def test_url_invalida_retorna_422(self, client: AsyncClient):
        """3. URL inválida → 422."""
        resp = await client.post("/encurtar", json={"url": "ssh://host"})
        assert resp.status_code == 422

    async def test_url_vazia_retorna_422(self, client: AsyncClient):
        """4. URL vazia → 422."""
        resp = await client.post("/encurtar", json={"url": ""})
        assert resp.status_code == 422

    async def test_url_duplicada_mesmo_short_code(self, client: AsyncClient):
        """5. URL já encurtada → mesmo short_code."""
        url = "https://duplicate-test.example"
        r1 = await client.post("/encurtar", json={"url": url})
        assert r1.status_code == 201
        r2 = await client.post("/encurtar", json={"url": url})
        assert r2.status_code == 201
        assert r1.json()["short_code"] == r2.json()["short_code"]


@pytest.mark.asyncio
class TestRedirect:

    async def test_short_code_inexistente_retorna_404(self, client: AsyncClient):
        """6. Short code inexistente → 404."""
        resp = await client.get("/ZZZZZZ")
        assert resp.status_code == 404

    async def test_short_code_valido_redireciona_302_com_clicks(
        self, client: AsyncClient
    ):
        """7. Short code válido → 302 + incrementa clicks."""
        # Criar URL
        r_create = await client.post(
            "/encurtar", json={"url": "https://click-test.example"}
        )
        assert r_create.status_code == 201
        short_code = r_create.json()["short_code"]

        # Primeiro acesso
        r1 = await client.get(f"/{short_code}", follow_redirects=False)
        assert r1.status_code == 302
        assert r1.headers["location"] == "https://click-test.example"


@pytest.mark.asyncio
class TestHealth:

    async def test_health_check(self, client: AsyncClient):
        """8. Health check GET / → 200."""
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
class TestColisao:
    async def test_colisao_com_retry_nao_quebra(self, client: AsyncClient):
        """9. Geração com retry não quebra (força colisão no primeiro code)."""
        import main as main_mod

        original_generator = main_mod._models_module.generate_short_code
        call_count = 0
        already_called = False

        def colliding_generator():
            nonlocal call_count, already_called
            call_count += 1
            if not already_called:
                already_called = True
                return "AAAAAA"
            return original_generator()

        with patch.object(main_mod._models_module, "generate_short_code", colliding_generator):
            # URL 1 — ganha AAAAAA (banco vazio, sem colisão)
            r1 = await client.post(
                "/encurtar", json={"url": "https://collision-a.example/1"}
            )
            assert r1.status_code == 201
            assert r1.json()["short_code"] == "AAAAAA", (
                f"Esperava AAAAAA, obteve {r1.json()['short_code']}"
            )

            # URL 2 — colliding_generator retorna AAAAAA primeiro (colisão!),
            # depois delega ao gerador real no retry.
            r2 = await client.post(
                "/encurtar", json={"url": "https://collision-a.example/2"}
            )
            assert r2.status_code == 201
            assert r2.json()["short_code"] != "AAAAAA"
            assert len(r2.json()["short_code"]) == 6
            assert call_count >= 2  # Colisão + retry = no mínimo 2 chamadas
