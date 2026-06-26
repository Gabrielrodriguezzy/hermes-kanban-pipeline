"""Test to debug the collision mock."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

# Force fresh reimport of main and models
import sys
for mod in list(sys.modules.keys()):
    if 'encurtador-url' in mod or 'main' in mod or 'model' in mod or 'database' in mod:
        del sys.modules[mod]

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

@pytest.mark.asyncio
async def test_debug_mock(client: AsyncClient):
    import main as main_mod
    import models

    print(f"\nmodels.id={id(models)} main_mod._models_module.id={id(main_mod._models_module)} same={models is main_mod._models_module}")

    original = models.generate_short_code
    models.generate_short_code = lambda: "AAAAAA"

    r1 = await client.post("/encurtar", json={"url": "https://test.example"})
    print(f"status={r1.status_code} body={r1.json()}")

    models.generate_short_code = original

    assert r1.status_code == 201
    assert r1.json()["short_code"] == "AAAAAA", f"Got {r1.json()['short_code']}"
