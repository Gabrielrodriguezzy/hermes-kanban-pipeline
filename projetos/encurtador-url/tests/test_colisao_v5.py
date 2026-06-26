"""Test: patch BEFORE main is imported, inside conftest-like pattern."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

# Import main AFTER patch setup — but that would affect ALL tests.
# Instead, let's patch at the models module attribute level using monkeypatch
# and verify the attribute truly changed.

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
        import models

        # Verify before monkeypatch
        print(f"\nBefore monkeypatch:")
        print(f"  models.generate_short_code id={id(models.generate_short_code)}")
        print(f"  main_mod._models_module.generate_short_code id={id(main_mod._models_module.generate_short_code)}")
        print(f"  same object: {models.generate_short_code is main_mod._models_module.generate_short_code}")

        # Record what models.generate_short_code references BEFORE we change it
        original_code = main_mod._models_module.generate_short_code
        call_count = 0

        def fake():
            nonlocal call_count
            call_count += 1
            return "AAAAAA" if call_count == 1 else original_code()

        monkeypatch.setattr(main_mod._models_module, "generate_short_code", fake)

        print(f"\nAfter monkeypatch:")
        print(f"  models.generate_short_code id={id(models.generate_short_code)}")
        print(f"  main_mod._models_module.generate_short_code id={id(main_mod._models_module.generate_short_code)}")
        print(f"  are they same? {models.generate_short_code is main_mod._models_module.generate_short_code}")

        # Direct call test
        result_direct = main_mod._models_module.generate_short_code()
        print(f"  Direct call result: {result_direct}, call_count={call_count}")

        r1 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/1"}
        )
        sc = r1.json()["short_code"]
        print(f"\nHTTP response: short_code={sc}, call_count={call_count}")
        assert r1.status_code == 201
        assert sc == "AAAAAA", f"Got {sc}"

        r2 = await client.post(
            "/encurtar", json={"url": "https://collision-a.example/2"}
        )
        assert r2.status_code == 201
        assert r2.json()["short_code"] != "AAAAAA"
        assert call_count >= 2
