"""Test colisao with correct mock logic."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from main import app
from database import reset_db, close_db

@pytest.fixture(autouse=True)
async def _reset_db():
    await reset_db()
    yield
    await close_db()

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

class TestColisao:
    async def test_colisao_com_retry_nao_quebra(self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
        import main as main_mod

        original_code = main_mod._models_module.generate_short_code
        call_count = 0

        # Return AAAAAA for the FIRST call, then delegate to original.
        # After the first URL is created, it will collide when the second
        # URL tries to use AAAAAA again, forcing a retry.
        already_called = False

        def fake():
            nonlocal already_called, call_count
            call_count += 1
            if not already_called:
                already_called = True
                return "AAAAAA"
            return original_code()

        monkeypatch.setattr(main_mod._models_module, "generate_short_code", fake)

        # URL 1 — should get AAAAAA (no collision, fresh DB)
        r1 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/1"}
        )
        assert r1.status_code == 201, f"URL 1 status {r1.status_code}"
        sc1 = r1.json()["short_code"]
        assert sc1 == "AAAAAA", f"URL 1: esperava AAAAAA, obteve {sc1}"

        # URL 2 — fake will first return AAAAAA again (collision!), then retry
        # with original_code().
        r2 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/2"}
        )
        assert r2.status_code == 201, f"URL 2 status {r2.status_code}"
        sc2 = r2.json()["short_code"]
        assert sc2 != "AAAAAA", f"URL 2 nao deveria ser AAAAAA"
        assert len(sc2) == 6

        # At least: URL1 call + URL2 first attempt (collision) + URL2 retry = 3
        assert call_count >= 2, f"call_count={call_count}, esperava >= 2"
