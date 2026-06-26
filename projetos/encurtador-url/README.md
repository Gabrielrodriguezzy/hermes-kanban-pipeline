# URL Shortener API

A production-grade URL shortener built with FastAPI and async SQLite.

## Features

- **Shorten URLs** — POST `/encurtar` with a long URL, get a 6-character short code
- **Redirect** — GET `/{short_code}` redirects (302) to the original URL
- **Statistics** — GET `/stats/{short_code}` returns click count and metadata
- **Health check** — GET `/` returns `{"status": "ok"}`
- **Deduplication** — same URL always returns the same short code
- **Collision-resistant** — retries with different codes on hash collision (up to 5 attempts)
- **Async throughout** — uses SQLAlchemy async + aiosqlite for non-blocking I/O

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python 3.11) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via aiosqlite |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio + httpx |

## Quick Start

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

The API serves at `http://localhost:8000`.

## API Endpoints

### `POST /encurtar`

Create a short URL.

```json
// Request
{"url": "https://example.com/very/long/path"}

// Response (201)
{
  "short_code": "aB3xYz",
  "short_url": "http://localhost:8000/aB3xYz",
  "original_url": "https://example.com/very/long/path"
}
```

Validation rules:
- URL must have a scheme (`https://`, `http://`)
- Only `http`, `https`, `ftp` schemes allowed

### `GET /{short_code}`

Redirect to the original URL (HTTP 302).

| Response | Meaning |
|----------|---------|
| 302 | Redirect to original URL |
| 404 | Short code not found |

### `GET /stats/{short_code}`

Get statistics for a short URL.

```json
// Response (200)
{
  "short_code": "aB3xYz",
  "original_url": "https://example.com/very/long/path",
  "clicks": 42,
  "created_at": "2026-01-15T10:30:00"
}
```

### `GET /`

Health check.

```json
// Response (200)
{"status": "ok"}
```

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

All 9 tests cover:

1. Normal URL generates valid 6-char short code
2. URL without scheme returns 422
3. Invalid URL returns 422
4. Empty URL returns 422
5. Duplicate URL returns same short code
6. Non-existent short code returns 404
7. Valid short code redirects 302 and increments clicks
8. Health check returns 200
9. Hash collision with retry doesn't break

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./urls.db` | Database connection string |

## Project Structure

```
encurtador-url/
├── main.py              # FastAPI application + endpoints
├── models.py            # SQLAlchemy ORM model + Pydantic schemas
├── database.py          # Async engine, session factory, init/close
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Pytest configuration
└── tests/
    └── test_main.py     # 9 integration tests
```
