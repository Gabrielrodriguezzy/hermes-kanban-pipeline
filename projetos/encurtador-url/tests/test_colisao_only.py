"""Test only the colisao test with no event_loop fixture."""
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
    async def test_colisao_com_retry_nao_quebra(self, client: AsyncClient):
        from unittest.mock import patch
        import main as main_mod

        call_count = 0
        original_generator = main_mod._models_module.generate_short_code

        def colliding_generator():
            nonlocal call_count
            call_count += 1
            return "AAAAAA" if call_count == 1 else original_generator()

        with patch.object(main_mod._models_module, "generate_short_code", colliding_generator):
            r1 = await client.post(
                "/encurtar", json={"url": "https://collision-a.example/1"}
            )
            assert r1.status_code == 201
            assert r1.json()["short_code"] == "AAAAAA", (
                f"Esperava AAAAAA, obteve {r1.json()['short_code']}"
            )

            r2 = await client.post(
                "/encurtar", json={"url": "https://collision-a.example/2"}
            )
            assert r2.status_code == 201
            assert r2.json()["short_code"] != "AAAAAA"
            assert len(r2.json()["short_code"]) == 6
            assert call_count >= 2
