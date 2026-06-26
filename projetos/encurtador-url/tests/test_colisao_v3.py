"""Test with monkeypatch."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from database import init_db, close_db

@pytest.fixture(autouse=True)
async def _reset_db():
    await init_db()
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
        call_count = 0
        original = main_mod._models_module.generate_short_code

        def fake():
            nonlocal call_count
            call_count += 1
            return "AAAAAA" if call_count == 1 else original()

        monkeypatch.setattr(main_mod._models_module, "generate_short_code", fake)

        r1 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/1"}
        )
        print(f"DEBUG: short_code={r1.json()['short_code']} call_count={call_count}")
        assert r1.status_code == 201
        assert r1.json()["short_code"] == "AAAAAA", f"Got {r1.json()['short_code']}"

        r2 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/2"}
        )
        assert r2.status_code == 201
        assert r2.json()["short_code"] != "AAAAAA"
        assert call_count >= 2
