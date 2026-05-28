# Phase 0 — Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the `finacialsim-saas` repo with FastAPI + React + Postgres + Redis + Docker + CI all wired and a vendored `finacialsim_core` package importable, so Phase 1 can begin feature work immediately.

**Architecture:** FastAPI modular monolith behind a Caddy reverse proxy; React SPA built static and served by Caddy; ARQ worker on Redis; Postgres 16. All wired in docker-compose. Tests use testcontainers for a real Postgres.

**Tech Stack:** Python 3.12, uv, FastAPI 0.110+, SQLAlchemy 2 async, Alembic, ARQ, pydantic-settings, loguru, testcontainers-python; React 18, Vite, TypeScript, Tailwind, shadcn/ui, TanStack Query, React Router, Vitest.

> **Important:** All file paths below are relative to the root of the NEW `finacialsim-saas` repo. Work outside the current `finacialsim` repo.

---

## File Map

```
finacialsim-saas/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/001_create_tenants.py
│   ├── finacialsim_saas/
│   │   ├── __init__.py
│   │   ├── settings.py          — pydantic-settings Settings model
│   │   ├── errors.py            — typed domain error classes
│   │   ├── main.py              — FastAPI app + exception handler + lifespan
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── database.py      — async engine + session factory
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── health.py        — /healthz, /version routers
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── logging.py       — request_id + structured JSON log middleware
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── tasks.py         — ARQ task functions (ping)
│   │       └── worker.py        — ARQ WorkerSettings
│   └── tests/
│       ├── conftest.py           — testcontainers Postgres fixture
│       ├── test_health.py
│       └── test_worker.py
├── packages/
│   └── finacialsim_core/
│       ├── pyproject.toml
│       ├── finacialsim_core/
│       │   ├── __init__.py
│       │   ├── core/            — copied from finacialsim/app/core/
│       │   ├── integrations/    — copied from finacialsim/app/integrations/
│       │   ├── reports/         — copied from finacialsim/app/reports/
│       │   └── utils/
│       │       └── document_validation.py
│       └── tests/               — copied from finacialsim/tests/unit/core/ + integrations/
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── lib/api.ts           — axios client
│       ├── routes/
│       │   ├── Index.tsx        — renders shadcn Button
│       │   └── Health.tsx       — calls /healthz, shows result
│       └── tests/
│           └── App.test.tsx
├── ops/
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.web
│   ├── nginx.conf
│   ├── docker-compose.yml
│   └── Caddyfile
├── .github/
│   └── workflows/ci.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Task 1: Repo skeleton + Python package setup

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/finacialsim_saas/__init__.py`
- Create: `.gitignore`

- [ ] **Step 1: Bootstrap the repo**

```bash
# Run from the PARENT directory of finacialsim/
mkdir finacialsim-saas && cd finacialsim-saas
git init
mkdir -p backend/finacialsim_saas frontend packages/finacialsim_core ops .github/workflows docs
```

- [ ] **Step 2: Write `backend/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "finacialsim-saas"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "alembic>=1.13.0",
    "asyncpg>=0.29.0",
    "pydantic-settings>=2.2.0",
    "loguru>=0.7.0",
    "arq>=0.25.0",
    "redis>=5.0.0",
    "finacialsim-core",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
    "testcontainers[postgres]>=4.7.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
]

[tool.uv.sources]
finacialsim-core = { path = "../packages/finacialsim_core", editable = true }

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
```

- [ ] **Step 3: Write `backend/finacialsim_saas/__init__.py`**

```python
"""FinacialSim SaaS backend."""
```

- [ ] **Step 4: Write `.gitignore`**

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
*.egg-info/
dist/
.mypy_cache/
.ruff_cache/
.pytest_cache/
htmlcov/
node_modules/
.DS_Store
*.local
```

- [ ] **Step 5: Install deps with uv**

```bash
cd backend
uv venv .venv
uv pip install -e ".[dev]"
```

Expected: resolves without errors (`finacialsim-core` will fail until Task 9 — that's fine for now).

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "chore: initialize finacialsim-saas repo skeleton"
```

---

## Task 2: Settings model + `.env.example`

**Files:**
- Create: `backend/finacialsim_saas/settings.py`
- Create: `.env.example`
- Create: `backend/tests/test_settings.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/settings.py`**

```python
from typing import Literal
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: PostgresDsn

    # Redis
    redis_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore[assignment]

    # App
    app_env: Literal["development", "production", "test"] = "development"
    app_secret_key: str = "change-me-in-production"

    # Build info (injected at Docker build time)
    git_sha: str = "dev"
    build_time: str = ""

    # Sentry (optional — off when unset)
    sentry_dsn: str | None = None

    # Storage
    storage_backend: Literal["local", "s3"] = "local"
    storage_local_root: str = "/var/lib/finacialsim/objects"

    # Worker
    worker_concurrency: int = 4


def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 2: Write `backend/tests/test_settings.py`**

```python
import pytest
from finacialsim_saas.settings import Settings


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    s = Settings()
    assert s.app_env == "development"
    assert s.git_sha == "dev"
    assert s.sentry_dsn is None


def test_settings_rejects_missing_database_url():
    with pytest.raises(Exception):
        Settings(_env_file=None)  # type: ignore[call-arg]
```

- [ ] **Step 3: Run test**

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://u:p@localhost/db APP_SECRET_KEY=test \
  python -m pytest tests/test_settings.py -v
```

Expected: `2 passed`

- [ ] **Step 4: Write `.env.example`**

```dotenv
# ── Database ──────────────────────────────────────────────────────────────────
# PostgreSQL connection string. Use asyncpg driver.
DATABASE_URL=postgresql+asyncpg://finacialsim:changeme@db:5432/finacialsim

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── App ───────────────────────────────────────────────────────────────────────
APP_ENV=development
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
APP_SECRET_KEY=change-me-in-production

# ── Build info (injected at Docker build time — leave blank for local dev) ────
GIT_SHA=dev
BUILD_TIME=

# ── Sentry (optional — leave blank to disable) ────────────────────────────────
SENTRY_DSN=

# ── Storage ───────────────────────────────────────────────────────────────────
STORAGE_BACKEND=local
STORAGE_LOCAL_ROOT=/var/lib/finacialsim/objects
# S3 — only used when STORAGE_BACKEND=s3
# S3_BUCKET=
# S3_ENDPOINT_URL=
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_REGION=us-east-1

# ── Worker ────────────────────────────────────────────────────────────────────
WORKER_CONCURRENCY=4
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: Settings model and .env.example"
```

---

## Task 3: Typed error classes

**Files:**
- Create: `backend/finacialsim_saas/errors.py`
- Create: `backend/tests/test_errors.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/errors.py`**

```python
from typing import Any


class AppError(Exception):
    code: str = "app_error"
    status_code: int = 500

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(AppError):
    code = "validation_error"
    status_code = 422


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class ConflictError(AppError):
    code = "conflict"
    status_code = 409


class AuthError(AppError):
    code = "auth_error"
    status_code = 401


class TenantAccessError(AppError):
    code = "tenant_access_error"
    status_code = 403


class ExternalProviderError(AppError):
    code = "external_provider_error"
    status_code = 502

    def __init__(self, message: str, details: Any = None, degraded: bool = False) -> None:
        super().__init__(message, details)
        self.degraded = degraded
```

- [ ] **Step 2: Write `backend/tests/test_errors.py`**

```python
from finacialsim_saas.errors import (
    AppError, NotFoundError, ConflictError, AuthError,
    TenantAccessError, ExternalProviderError, ValidationError,
)


def test_not_found_has_correct_code():
    err = NotFoundError("simulation not found")
    assert err.code == "not_found"
    assert err.status_code == 404
    assert err.message == "simulation not found"


def test_external_provider_error_degraded():
    err = ExternalProviderError("FIPE unreachable", degraded=True)
    assert err.degraded is True
    assert err.status_code == 502


def test_all_errors_are_app_errors():
    for cls in [NotFoundError, ConflictError, AuthError,
                TenantAccessError, ExternalProviderError, ValidationError]:
        assert issubclass(cls, AppError)
```

- [ ] **Step 3: Run tests**

```bash
cd backend
python -m pytest tests/test_errors.py -v
```

Expected: `3 passed`

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: typed domain error classes"
```

---

## Task 4: Database setup (async SQLAlchemy + testcontainers fixture)

**Files:**
- Create: `backend/finacialsim_saas/data/__init__.py`
- Create: `backend/finacialsim_saas/data/database.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/data/database.py`**

```python
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def check_db(engine: AsyncEngine) -> bool:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True
```

- [ ] **Step 2: Write `backend/tests/conftest.py`**

```python
import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from finacialsim_saas.data.database import Base, build_engine, build_session_factory


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def db_url(postgres_container):
    url = postgres_container.get_connection_url()
    return url.replace("psycopg2", "asyncpg").replace("postgresql://", "postgresql+asyncpg://")


@pytest_asyncio.fixture(scope="session")
async def engine(db_url) -> AsyncEngine:
    eng = build_engine(db_url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    factory = build_session_factory(engine)
    async with factory() as s:
        yield s
        await s.rollback()
```

- [ ] **Step 3: Write `backend/tests/test_database.py`**

```python
import pytest
from sqlalchemy import text
from finacialsim_saas.data.database import check_db


@pytest.mark.asyncio
async def test_db_ping(engine):
    result = await check_db(engine)
    assert result is True


@pytest.mark.asyncio
async def test_session_executes(session):
    result = await session.execute(text("SELECT 42 AS answer"))
    row = result.fetchone()
    assert row is not None
    assert row.answer == 42
```

- [ ] **Step 4: Run tests**

```bash
cd backend
python -m pytest tests/test_database.py -v
```

Expected: `2 passed` (testcontainers downloads `postgres:16-alpine` on first run)

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: async SQLAlchemy engine + testcontainers conftest"
```

---

## Task 5: Alembic setup + first migration (tenants table)

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_create_tenants.py`

- [ ] **Step 1: Initialize Alembic**

```bash
cd backend
uv run alembic init alembic
```

- [ ] **Step 2: Replace `backend/alembic/env.py` with the async version**

```python
import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from finacialsim_saas.data.database import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return os.environ["DATABASE_URL"]


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):  # type: ignore[no-untyped-def]
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()
    connectable = async_engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Write `backend/alembic/versions/001_create_tenants.py`**

```python
"""create tenants table

Revision ID: 001
Revises:
Create Date: 2026-05-28
"""
import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column(
            "id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )


def downgrade() -> None:
    op.drop_table("tenants")
```

- [ ] **Step 4: Test migration against a temporary Postgres**

```bash
docker run -d --name pg-test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=fsim \
  -p 5433:5432 postgres:16-alpine
sleep 3
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:test@localhost:5433/fsim \
  uv run alembic upgrade head
docker stop pg-test && docker rm pg-test
```

Expected: `Running upgrade -> 001, create tenants table` with no errors.

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: Alembic + 001 create tenants migration"
```

---

## Task 6: FastAPI app + `/healthz` + `/version` + exception handler

**Files:**
- Create: `backend/finacialsim_saas/api/__init__.py`
- Create: `backend/finacialsim_saas/api/health.py`
- Create: `backend/finacialsim_saas/main.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/api/health.py`**

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter()


@router.get("/healthz")
async def healthz():
    from finacialsim_saas.main import app_state
    try:
        async with app_state["engine"].connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as exc:
        return JSONResponse(status_code=503, content={"status": "error", "db": str(exc)})


@router.get("/version")
async def version():
    from finacialsim_saas.settings import get_settings
    s = get_settings()
    return {"git_sha": s.git_sha, "build_time": s.build_time, "app_env": s.app_env}
```

- [ ] **Step 2: Write `backend/finacialsim_saas/main.py`**

```python
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from finacialsim_saas.data.database import build_engine
from finacialsim_saas.errors import AppError
from finacialsim_saas.settings import get_settings

app_state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = build_engine(str(settings.database_url))
    app_state["engine"] = engine
    logger.info("Startup complete", env=settings.app_env)
    yield
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(title="FinacialSim SaaS", lifespan=lifespan)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    import time
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request",
            route=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


from finacialsim_saas.api.health import router as health_router  # noqa: E402
app.include_router(health_router)
```

- [ ] **Step 3: Write `backend/tests/test_health.py`**

```python
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def client(engine):
    from finacialsim_saas.main import app, app_state
    app_state["engine"] = engine
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_healthz_returns_ok(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}


@pytest.mark.asyncio
async def test_version_returns_git_sha(client):
    response = await client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "git_sha" in data
    assert "app_env" in data


@pytest.mark.asyncio
async def test_app_error_handler(client):
    from fastapi import APIRouter
    from finacialsim_saas.errors import NotFoundError
    from finacialsim_saas.main import app

    test_router = APIRouter()

    @test_router.get("/test-error")
    async def raise_error():
        raise NotFoundError("thing not found")

    app.include_router(test_router)
    response = await client.get("/test-error")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert "request_id" in response.json()
```

- [ ] **Step 4: Run tests**

```bash
cd backend
python -m pytest tests/test_health.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: FastAPI app with /healthz, /version, AppError handler"
```

---

## Task 7: Structured JSON logging

**Files:**
- Create: `backend/finacialsim_saas/middleware/__init__.py`
- Create: `backend/finacialsim_saas/middleware/logging.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/middleware/logging.py`**

```python
import sys
from loguru import logger


def configure_logging(app_env: str = "development") -> None:
    logger.remove()
    if app_env == "production":
        logger.add(sys.stdout, format="{message}", serialize=True, level="INFO")
    else:
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
            level="DEBUG",
            colorize=True,
        )
```

- [ ] **Step 2: Call `configure_logging` in `main.py` lifespan**

Update the top of the `lifespan` function in `backend/finacialsim_saas/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    from finacialsim_saas.middleware.logging import configure_logging
    settings = get_settings()
    configure_logging(settings.app_env)
    engine = build_engine(str(settings.database_url))
    app_state["engine"] = engine
    logger.info("Startup complete", env=settings.app_env)
    yield
    await engine.dispose()
    logger.info("Shutdown complete")
```

- [ ] **Step 3: Verify all tests still pass**

```bash
cd backend
python -m pytest tests/ -v
```

Expected: all existing tests pass.

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: structured JSON logging with request_id and latency"
```

---

## Task 8: ARQ worker + `ping` job

**Files:**
- Create: `backend/finacialsim_saas/workers/__init__.py`
- Create: `backend/finacialsim_saas/workers/tasks.py`
- Create: `backend/finacialsim_saas/workers/worker.py`
- Create: `backend/tests/test_worker.py`

- [ ] **Step 1: Write `backend/finacialsim_saas/workers/tasks.py`**

```python
from loguru import logger


async def ping(ctx: dict) -> str:
    """Health-check job — proves the worker is alive."""
    logger.info("ping job executed")
    return "pong"
```

- [ ] **Step 2: Write `backend/finacialsim_saas/workers/worker.py`**

```python
from arq.connections import RedisSettings
from finacialsim_saas.settings import get_settings
from finacialsim_saas.workers.tasks import ping


def get_redis_settings() -> RedisSettings:
    s = get_settings()
    return RedisSettings.from_dsn(str(s.redis_url))


class WorkerSettings:
    functions = [ping]
    redis_settings = get_redis_settings()
    max_jobs = 10
    job_timeout = 30
```

- [ ] **Step 3: Write `backend/tests/test_worker.py`**

```python
import pytest
from finacialsim_saas.workers.tasks import ping


@pytest.mark.asyncio
async def test_ping_returns_pong():
    result = await ping({})
    assert result == "pong"
```

- [ ] **Step 4: Run test**

```bash
cd backend
python -m pytest tests/test_worker.py -v
```

Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: ARQ worker scaffold with ping() job"
```

---

## Task 9: Vendor `finacialsim_core`

**Files:**
- Create: `packages/finacialsim_core/pyproject.toml`
- Create: `packages/finacialsim_core/finacialsim_core/` (copied from desktop)

- [ ] **Step 1: Write `packages/finacialsim_core/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "finacialsim-core"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0.0",
    "httpx>=0.27.0",
    "tenacity>=8.0.0",
    "jinja2>=3.1.0",
    "weasyprint>=62.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "hypothesis>=6.0.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Copy files from desktop repo**

Run from `finacialsim-saas/` root (adjust `../finacialsim` to the actual relative path to the desktop repo):

```bash
DESKTOP=../finacialsim
CORE=packages/finacialsim_core/finacialsim_core

mkdir -p $CORE/core $CORE/integrations/fipe $CORE/integrations/bacen \
          $CORE/reports $CORE/utils packages/finacialsim_core/tests

cp -r $DESKTOP/app/core/.           $CORE/core/
cp    $DESKTOP/app/integrations/base.py    $CORE/integrations/
cp    $DESKTOP/app/integrations/http.py    $CORE/integrations/
cp    $DESKTOP/app/integrations/factory.py $CORE/integrations/
cp -r $DESKTOP/app/integrations/fipe/.    $CORE/integrations/fipe/
cp -r $DESKTOP/app/integrations/bacen/.   $CORE/integrations/bacen/
cp -r $DESKTOP/app/reports/.              $CORE/reports/
cp    $DESKTOP/app/utils/document_validation.py $CORE/utils/
cp -r $DESKTOP/tests/unit/core/.          packages/finacialsim_core/tests/core/
cp -r $DESKTOP/tests/unit/integrations/.  packages/finacialsim_core/tests/integrations/

touch $CORE/__init__.py \
      $CORE/core/__init__.py \
      $CORE/integrations/__init__.py \
      $CORE/integrations/fipe/__init__.py \
      $CORE/integrations/bacen/__init__.py \
      $CORE/utils/__init__.py \
      packages/finacialsim_core/tests/__init__.py
```

- [ ] **Step 3: Verify no forbidden imports**

```bash
grep -r "nicegui\|from app\.data\|from app\.ui\|from sqlalchemy" \
  packages/finacialsim_core/finacialsim_core/ || echo "CLEAN"
```

Expected: `CLEAN`. If any matches appear, remove or stub those imports before continuing.

- [ ] **Step 4: Run vendored tests**

```bash
cd packages/finacialsim_core
uv venv .venv && uv pip install -e ".[dev]"
python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected: all tests from the desktop repo pass unchanged.

- [ ] **Step 5: Verify importable from backend**

```bash
cd backend
uv pip install -e ".[dev]"
python -c "from finacialsim_core.core.price_table import build_schedule; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: vendor finacialsim_core with full test suite"
```

---

## Task 10: Frontend scaffold

**Files:**
- Create: `frontend/` (via `npm create vite`)
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/routes/Index.tsx`
- Create: `frontend/src/routes/Health.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/tests/setup.ts`
- Create: `frontend/src/tests/App.test.tsx`

- [ ] **Step 1: Scaffold Vite app**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

- [ ] **Step 2: Install deps**

```bash
npm install @tanstack/react-query react-router-dom axios \
  tailwindcss @tailwindcss/vite clsx tailwind-merge

npm install -D vitest @vitest/ui @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event jsdom \
  eslint @eslint/js typescript-eslint prettier

npx shadcn@latest init --yes --defaults
npx shadcn@latest add button
```

- [ ] **Step 3: Write `frontend/src/lib/api.ts`**

```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  withCredentials: true,
});
```

- [ ] **Step 4: Write `frontend/src/routes/Index.tsx`**

```typescript
import { Button } from "@/components/ui/button";

export default function Index() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Button variant="default">FinacialSim SaaS</Button>
    </div>
  );
}
```

- [ ] **Step 5: Write `frontend/src/routes/Health.tsx`**

```typescript
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function Health() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["healthz"],
    queryFn: () => api.get("/healthz").then((r) => r.data),
  });
  if (isLoading) return <p>Checking…</p>;
  if (isError) return <p className="text-red-500">API unreachable</p>;
  return <pre className="p-4 bg-gray-100 rounded">{JSON.stringify(data, null, 2)}</pre>;
}
```

- [ ] **Step 6: Write `frontend/src/App.tsx`**

```typescript
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Index from "./routes/Index";
import Health from "./routes/Health";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/healthz" element={<Health />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

- [ ] **Step 7: Write `frontend/src/tests/setup.ts`**

```typescript
import "@testing-library/jest-dom";
```

- [ ] **Step 8: Write `frontend/src/tests/App.test.tsx`**

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Index from "../routes/Index";

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>
    <MemoryRouter>{children}</MemoryRouter>
  </QueryClientProvider>
);

describe("Index route", () => {
  it("renders the FinacialSim button", () => {
    render(<Index />, { wrapper });
    expect(screen.getByRole("button", { name: /FinacialSim SaaS/i })).toBeDefined();
  });
});
```

- [ ] **Step 9: Update `frontend/vite.config.ts`**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/tests/setup.ts"],
  },
});
```

- [ ] **Step 10: Run frontend tests**

```bash
cd frontend
npm test -- --run
```

Expected: `1 test passed`

- [ ] **Step 11: Commit**

```bash
git add .
git commit -m "feat: React + Vite + Tailwind + shadcn/ui frontend scaffold"
```

---

## Task 11: Docker + docker-compose

**Files:**
- Create: `ops/Dockerfile.api`
- Create: `ops/Dockerfile.worker`
- Create: `ops/Dockerfile.web`
- Create: `ops/nginx.conf`
- Create: `ops/docker-compose.yml`
- Create: `ops/Caddyfile`

- [ ] **Step 1: Write `ops/Dockerfile.api`**

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install uv
COPY backend/pyproject.toml backend/
COPY packages/ packages/
RUN cd backend && uv pip install --system --no-cache ".[dev]"

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY backend/ .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "finacialsim_saas.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Write `ops/Dockerfile.worker`**

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install uv
COPY backend/pyproject.toml backend/
COPY packages/ packages/
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
RUN cd backend && uv pip install --system --no-cache ".[dev]"

FROM python:3.12-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY backend/ .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "arq", "finacialsim_saas.workers.worker.WorkerSettings"]
```

- [ ] **Step 3: Write `ops/Dockerfile.web`**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY ops/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

- [ ] **Step 4: Write `ops/nginx.conf`**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 5: Write `ops/Caddyfile`**

```caddy
:80 {
    handle /api/* {
        uri strip_prefix /api
        reverse_proxy api:8000
    }
    handle {
        reverse_proxy web:80
    }
}
```

- [ ] **Step 6: Write `ops/docker-compose.yml`**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: finacialsim
      POSTGRES_USER: finacialsim
      POSTGRES_PASSWORD: changeme
    volumes:
      - pg-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U finacialsim"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 10

  migrate:
    build:
      context: ..
      dockerfile: ops/Dockerfile.api
    env_file: ../.env
    environment:
      DATABASE_URL: postgresql+asyncpg://finacialsim:changeme@db:5432/finacialsim
    command: alembic upgrade head
    depends_on:
      db:
        condition: service_healthy

  api:
    build:
      context: ..
      dockerfile: ops/Dockerfile.api
    env_file: ../.env
    environment:
      DATABASE_URL: postgresql+asyncpg://finacialsim:changeme@db:5432/finacialsim
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/healthz || exit 1"]
      interval: 10s
      retries: 6

  worker:
    build:
      context: ..
      dockerfile: ops/Dockerfile.worker
    env_file: ../.env
    environment:
      DATABASE_URL: postgresql+asyncpg://finacialsim:changeme@db:5432/finacialsim
      REDIS_URL: redis://redis:6379/0
    depends_on:
      api:
        condition: service_healthy

  web:
    build:
      context: ..
      dockerfile: ops/Dockerfile.web

  proxy:
    image: caddy:2-alpine
    ports:
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    depends_on:
      - api
      - web

volumes:
  pg-data:
  object-store:
```

- [ ] **Step 7: Build images**

```bash
cd ops
docker compose build
```

Expected: all three images build without error.

- [ ] **Step 8: Commit**

```bash
git add .
git commit -m "feat: Dockerfiles and docker-compose stack"
```

---

## Task 12: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
name: CI
on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install uv
      - run: uv pip install --system -e ".[dev]"
      - run: ruff check .
      - run: mypy finacialsim_saas
      - run: pytest tests/ --cov=finacialsim_saas --cov-report=term-missing
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test
          APP_SECRET_KEY: ci-secret

  vendored-core:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: packages/finacialsim_core
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install uv
      - run: uv pip install --system -e ".[dev]"
      - name: Verify no forbidden imports
        run: |
          grep -r "nicegui\|from app\.data\|from app\.ui\|from sqlalchemy" \
            finacialsim_core/ && exit 1 || echo "CLEAN"
      - run: pytest tests/ -v --tb=short

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npx eslint src/
      - run: npx tsc --noEmit
      - run: npm test -- --run

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -f ops/Dockerfile.api -t finacialsim-saas-api .
      - run: docker build -f ops/Dockerfile.worker -t finacialsim-saas-worker .
      - run: docker build -f ops/Dockerfile.web -t finacialsim-saas-web .
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "ci: GitHub Actions — backend, vendored-core, frontend, docker"
```

---

## Task 13: README + smoke test

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

````markdown
# FinacialSim SaaS

Web-accessible financing simulation platform for Brazilian vehicle dealerships.
Migrated from the desktop [finacialsim](../finacialsim) app.

**Spec:** `docs/superpowers/specs/2026-05-28-saas-roadmap.md`

## Quick start

```bash
cp .env.example .env        # review and adjust values
cd ops
docker compose run --rm migrate   # apply DB migrations
docker compose up
```

Open http://localhost — Caddy serves the React app and proxies `/api/*` to FastAPI.

## Development

```bash
# Backend
cd backend && uv pip install -e ".[dev]"
DATABASE_URL=postgresql+asyncpg://... APP_SECRET_KEY=dev pytest

# Frontend
cd frontend && npm install && npm run dev

# Vendored core
cd packages/finacialsim_core && uv pip install -e ".[dev]" && pytest
```

## ⚠ Connection pooler constraint

If you add pgBouncer or any external connection pooler, it **must** run in
**session mode** — never transaction mode. The RLS design uses
`SET LOCAL app.tenant_id` which only survives within a single connection
session. Transaction-mode pooling silently bypasses RLS.
````

- [ ] **Step 2: Full local smoke test**

```bash
cd ops
docker compose up --build -d
sleep 30
curl -s http://localhost/healthz | python3 -m json.tool
curl -s http://localhost/version | python3 -m json.tool
```

Expected output:
```json
{"status": "ok", "db": "ok"}
{"git_sha": "dev", "build_time": "", "app_env": "development"}
```

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "docs: README with quickstart and connection pooler constraint"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| New repo + uv + ruff + mypy + pytest | 1 |
| `Settings` model + `.env.example` | 2 |
| Typed error classes + exception handler | 3, 6 |
| Async SQLAlchemy + testcontainers Postgres fixture | 4 |
| Alembic + `tenants` migration | 5 |
| `/healthz` (DB ping) + `/version` (git SHA) | 6 |
| Structured JSON logs + `request_id` middleware | 7 |
| ARQ worker + `ping()` + unit test | 8 |
| `finacialsim_core` vendored + forbidden-import check + tests | 9 |
| React + Vite + TS + shadcn/ui + TanStack Query + React Router | 10 |
| Dockerfiles (api, worker, web) + docker-compose + Caddy | 11 |
| CI (backend lint/type/test, core forbidden-import + test, frontend lint/type/test, docker build) | 12 |
| README + smoke test | 13 |
| Connection pooler constraint documented | 13 README |
| Worker processes a `ping` job (acceptance check 8) | 8 |

All acceptance checklist items covered. No TBDs or placeholders found.

---

Plan saved to `docs/superpowers/plans/2026-05-28-saas-phase-0-foundations.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — execute tasks in this session using executing-plans with checkpoints

**Which approach?**
