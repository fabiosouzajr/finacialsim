# Phase 3 — Integrações FIPE + BACEN

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`.

**Goal:** Implement the `integrations/` layer — `Provider` protocol + `ProviderChain` with fallback, FIPE providers (Parallelum + BrasilAPI + manual), BACEN providers (SGS + BrasilAPI), normalization, and caching.

**Architecture:** Each provider is an `async` class implementing the `Provider` protocol. The `ProviderChain` tries providers in order and returns the first valid response. Cache decorator wraps providers transparently using `fipe_cache` table.

**Tech Stack:** `httpx.AsyncClient`, `tenacity`, `respx` (test HTTP mocking), Pydantic v2 schemas.

**Dependencies:** Phase 1 (for `Decimal`) + Phase 2 (for `fipe_cache` table and `IndicatorRepository`).

---

## Task 1: `Result` type + `Provider` protocol + `ProviderChain`

**Files:**
- Create: `app/integrations/__init__.py` (empty)
- Create: `app/integrations/base.py`
- Create: `tests/unit/integrations/__init__.py` (empty)
- Create: `tests/unit/integrations/test_base.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/integrations/test_base.py`:
```python
import asyncio

import pytest

from app.integrations.base import Err, Ok, Provider, ProviderChain


class FakeProvider:
    def __init__(self, name: str, should_succeed: bool, payload: str = "ok"):
        self.name = name
        self.should_succeed = should_succeed
        self.payload = payload
        self.calls = 0

    async def fetch(self, query):
        self.calls += 1
        if self.should_succeed:
            return Ok(self.payload)
        return Err(f"{self.name} failed")


@pytest.mark.asyncio
async def test_chain_first_provider_wins():
    p1 = FakeProvider("p1", True, "from-p1")
    p2 = FakeProvider("p2", True, "from-p2")
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_ok
    assert result.value == "from-p1"
    assert p1.calls == 1
    assert p2.calls == 0


@pytest.mark.asyncio
async def test_chain_falls_back_to_second():
    p1 = FakeProvider("p1", False)
    p2 = FakeProvider("p2", True, "from-p2")
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_ok
    assert result.value == "from-p2"
    assert p1.calls == 1
    assert p2.calls == 1


@pytest.mark.asyncio
async def test_chain_all_fail_returns_err():
    p1 = FakeProvider("p1", False)
    p2 = FakeProvider("p2", False)
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/integrations/test_base.py -v`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

`app/integrations/base.py`:
```python
"""Provider protocol, Result type, and ProviderChain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    is_ok: bool = True
    is_err: bool = False


@dataclass(frozen=True)
class Err:
    error: str
    is_ok: bool = False
    is_err: bool = True


Result = Ok[T] | Err  # type: ignore[valid-type]


@runtime_checkable
class Provider(Protocol):
    name: str

    async def fetch(self, query: dict[str, Any]) -> "Ok[Any] | Err": ...


class ProviderChain:
    """Try each provider in order; first Ok wins. Logs failures."""

    def __init__(self, providers: list[Provider]) -> None:
        if not providers:
            raise ValueError("ProviderChain requires at least one provider")
        self.providers = providers

    async def fetch(self, query: dict[str, Any]) -> "Ok[Any] | Err":
        last_error = "no providers"
        for p in self.providers:
            result = await p.fetch(query)
            if result.is_ok:
                return result
            last_error = result.error  # type: ignore[union-attr]
        return Err(f"all_providers_failed: {last_error}")
```

- [ ] **Step 4: Install pytest-asyncio if missing**

Already in pyproject `dev` extras. Verify it's recognized:

Add to `pytest.ini`:
```ini
[pytest]
testpaths = tests
addopts = -ra --strict-markers
asyncio_mode = auto
markers =
    slow: tests that take >1s
    integration: integration tests across modules
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/integrations/ -v`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/integrations/ tests/unit/integrations/ pytest.ini
git commit -m "feat(integrations): Provider protocol + Result + ProviderChain"
```

---

## Task 2: FIPE `VehicleQuote` schema + Parallelum provider

**Files:**
- Create: `app/integrations/fipe/__init__.py` (empty)
- Create: `app/integrations/fipe/schema.py`
- Create: `app/integrations/fipe/parallelum.py`
- Create: `tests/unit/integrations/fipe/__init__.py`
- Create: `tests/unit/integrations/fipe/test_parallelum.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/integrations/fipe/test_parallelum.py`:
```python
from decimal import Decimal

import httpx
import pytest
import respx

from app.integrations.fipe.parallelum import ParallelumFipeProvider


@pytest.mark.asyncio
@respx.mock
async def test_get_brands_for_cars():
    respx.get("https://parallelum.com.br/fipe/api/v2/cars/brands").mock(
        return_value=httpx.Response(200, json=[
            {"code": "1", "name": "Acura"},
            {"code": "2", "name": "Agrale"},
        ])
    )
    p = ParallelumFipeProvider()
    result = await p.fetch({"action": "brands", "tipo": "cars"})
    assert result.is_ok
    brands = result.value
    assert len(brands) == 2
    assert brands[0]["name"] == "Acura"


@pytest.mark.asyncio
@respx.mock
async def test_get_price_parses_to_vehicle_quote():
    respx.get("https://parallelum.com.br/fipe/api/v2/cars/brands/21/models/1234/years/2024-1").mock(
        return_value=httpx.Response(200, json={
            "price": "R$ 45.230,00",
            "brand": "Fiat",
            "model": "Mobi 1.0",
            "modelYear": 2024,
            "fuel": "Gasolina",
            "codeFipe": "001234-5",
            "referenceMonth": "maio de 2026",
        })
    )
    p = ParallelumFipeProvider()
    result = await p.fetch({
        "action": "price", "tipo": "cars",
        "brand_id": "21", "model_id": "1234", "year_id": "2024-1",
    })
    assert result.is_ok
    quote = result.value
    assert quote.valor == Decimal("45230.00")
    assert quote.marca == "Fiat"
    assert quote.codigo_fipe == "001234-5"
    assert quote.fonte == "fipe_parallelum"


@pytest.mark.asyncio
@respx.mock
async def test_returns_err_on_500():
    respx.get("https://parallelum.com.br/fipe/api/v2/cars/brands").mock(
        return_value=httpx.Response(500)
    )
    p = ParallelumFipeProvider()
    result = await p.fetch({"action": "brands", "tipo": "cars"})
    assert result.is_err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/integrations/fipe/ -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write `schema.py`**

`app/integrations/fipe/schema.py`:
```python
"""FIPE normalized schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal


@dataclass(frozen=True)
class VehicleQuote:
    tipo: Literal["carro", "moto", "caminhao"]
    marca: str
    marca_id: str
    modelo: str
    modelo_id: str
    ano_modelo: int
    combustivel: str
    codigo_fipe: str
    valor: Decimal
    mes_referencia: str
    fonte: str
    raw_payload: dict[str, Any] = field(default_factory=dict)


def parse_brl_price(text: str) -> Decimal:
    """Parse 'R$ 45.230,00' -> Decimal('45230.00')."""
    cleaned = text.replace("R$", "").replace(".", "").replace(",", ".").strip()
    return Decimal(cleaned)
```

- [ ] **Step 4: Write Parallelum provider**

`app/integrations/fipe/parallelum.py`:
```python
"""FIPE Parallelum primary provider."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.base import Err, Ok
from app.integrations.fipe.schema import VehicleQuote, parse_brl_price


BASE_URL = "https://parallelum.com.br/fipe/api/v2"
TIPO_MAP = {"carro": "cars", "moto": "motorcycles", "caminhao": "trucks"}
REV_TIPO_MAP = {v: k for k, v in TIPO_MAP.items()}


class ParallelumFipeProvider:
    name = "fipe_parallelum"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def _get_json(self, path: str) -> dict[str, Any] | list[Any]:
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "FinacialSim/0.1"})
        try:
            resp = await client.get(f"{BASE_URL}{path}")
            resp.raise_for_status()
            return resp.json()
        finally:
            if owned:
                await client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=2))
    async def _fetch_raw(self, path: str) -> dict[str, Any] | list[Any]:
        return await self._get_json(path)

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        action = query.get("action")
        tipo = query.get("tipo")
        try:
            if action == "brands":
                data = await self._fetch_raw(f"/{tipo}/brands")
                return Ok(data)
            if action == "models":
                brand_id = query["brand_id"]
                data = await self._fetch_raw(f"/{tipo}/brands/{brand_id}/models")
                return Ok(data)
            if action == "years":
                brand_id = query["brand_id"]
                model_id = query["model_id"]
                data = await self._fetch_raw(f"/{tipo}/brands/{brand_id}/models/{model_id}/years")
                return Ok(data)
            if action == "price":
                brand_id = query["brand_id"]
                model_id = query["model_id"]
                year_id = query["year_id"]
                data = await self._fetch_raw(
                    f"/{tipo}/brands/{brand_id}/models/{model_id}/years/{year_id}"
                )
                quote = VehicleQuote(
                    tipo=REV_TIPO_MAP.get(tipo, "carro"),
                    marca=data["brand"],
                    marca_id=str(brand_id),
                    modelo=data["model"],
                    modelo_id=str(model_id),
                    ano_modelo=int(data["modelYear"]),
                    combustivel=data.get("fuel", ""),
                    codigo_fipe=data.get("codeFipe", ""),
                    valor=parse_brl_price(data["price"]),
                    mes_referencia=data.get("referenceMonth", ""),
                    fonte="fipe_parallelum",
                    raw_payload=data,
                )
                return Ok(quote)
            return Err(f"unknown_action: {action}")
        except httpx.HTTPError as e:
            return Err(f"http_error: {e}")
        except KeyError as e:
            return Err(f"missing_field: {e}")
        except Exception as e:
            return Err(f"unexpected: {e}")
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/integrations/fipe/ -v`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/integrations/fipe/ tests/unit/integrations/fipe/
git commit -m "feat(integrations): FIPE Parallelum provider + normalized schema"
```

---

## Task 3: FIPE BrasilAPI fallback provider

**Files:**
- Create: `app/integrations/fipe/brasilapi.py`
- Create: `tests/unit/integrations/fipe/test_brasilapi.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/integrations/fipe/test_brasilapi.py`:
```python
from decimal import Decimal

import httpx
import pytest
import respx

from app.integrations.fipe.brasilapi import BrasilApiFipeProvider


@pytest.mark.asyncio
@respx.mock
async def test_brasilapi_get_brands():
    respx.get("https://brasilapi.com.br/api/fipe/marcas/v1/carros").mock(
        return_value=httpx.Response(200, json=[
            {"valor": "1", "nome": "Acura"},
        ])
    )
    p = BrasilApiFipeProvider()
    result = await p.fetch({"action": "brands", "tipo": "carro"})
    assert result.is_ok
    assert result.value[0]["nome"] == "Acura"


@pytest.mark.asyncio
@respx.mock
async def test_brasilapi_get_price():
    respx.get("https://brasilapi.com.br/api/fipe/preco/v1/001234-5").mock(
        return_value=httpx.Response(200, json=[
            {
                "valor": "R$ 45.230,00",
                "marca": "Fiat",
                "modelo": "Mobi 1.0",
                "anoModelo": 2024,
                "combustivel": "Gasolina",
                "codigoFipe": "001234-5",
                "mesReferencia": "maio de 2026",
            }
        ])
    )
    p = BrasilApiFipeProvider()
    result = await p.fetch({
        "action": "price", "tipo": "carro", "codigo_fipe": "001234-5",
    })
    assert result.is_ok
    assert result.value.valor == Decimal("45230.00")
    assert result.value.fonte == "fipe_brasilapi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/integrations/fipe/test_brasilapi.py -v`
Expected: FAIL.

- [ ] **Step 3: Write implementation**

`app/integrations/fipe/brasilapi.py`:
```python
"""FIPE BrasilAPI fallback provider."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.base import Err, Ok
from app.integrations.fipe.schema import VehicleQuote, parse_brl_price


BASE_URL = "https://brasilapi.com.br/api/fipe"
TIPO_MAP = {"carro": "carros", "moto": "motos", "caminhao": "caminhoes"}


class BrasilApiFipeProvider:
    name = "fipe_brasilapi"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def _get_json(self, path: str) -> Any:
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "FinacialSim/0.1"})
        try:
            resp = await client.get(f"{BASE_URL}{path}")
            resp.raise_for_status()
            return resp.json()
        finally:
            if owned:
                await client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=2))
    async def _fetch_raw(self, path: str) -> Any:
        return await self._get_json(path)

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        try:
            action = query.get("action")
            tipo = query.get("tipo", "carro")
            ba_tipo = TIPO_MAP.get(tipo, "carros")
            if action == "brands":
                return Ok(await self._fetch_raw(f"/marcas/v1/{ba_tipo}"))
            if action == "price":
                codigo = query["codigo_fipe"]
                data = await self._fetch_raw(f"/preco/v1/{codigo}")
                if not data:
                    return Err("empty_response")
                d = data[0]
                quote = VehicleQuote(
                    tipo=tipo,
                    marca=d.get("marca", ""),
                    marca_id="",
                    modelo=d.get("modelo", ""),
                    modelo_id="",
                    ano_modelo=int(d.get("anoModelo", 0)),
                    combustivel=d.get("combustivel", ""),
                    codigo_fipe=d.get("codigoFipe", codigo),
                    valor=parse_brl_price(d["valor"]),
                    mes_referencia=d.get("mesReferencia", ""),
                    fonte="fipe_brasilapi",
                    raw_payload=d,
                )
                return Ok(quote)
            return Err(f"unsupported_action_for_brasilapi: {action}")
        except httpx.HTTPError as e:
            return Err(f"http_error: {e}")
        except Exception as e:
            return Err(f"unexpected: {e}")
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/integrations/fipe/ -v`
Expected: All FIPE tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/integrations/fipe/brasilapi.py tests/unit/integrations/fipe/test_brasilapi.py
git commit -m "feat(integrations): FIPE BrasilAPI fallback provider"
```

---

## Task 4: FIPE manual provider + FIPE cache layer

**Files:**
- Create: `app/integrations/fipe/manual.py`
- Create: `app/integrations/fipe/cache.py`
- Create: `tests/unit/integrations/fipe/test_manual.py`
- Create: `tests/unit/integrations/fipe/test_cache.py`

- [ ] **Step 1: Write `manual.py` (no API call, just constructs VehicleQuote from inputs)**

`app/integrations/fipe/manual.py`:
```python
"""Manual FIPE 'provider' - constructs a VehicleQuote from operator input."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.integrations.base import Err, Ok
from app.integrations.fipe.schema import VehicleQuote


class ManualFipeProvider:
    name = "fipe_manual"

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        if query.get("action") != "price":
            return Err("manual_only_supports_price")
        try:
            quote = VehicleQuote(
                tipo=query.get("tipo", "carro"),
                marca=query["marca"],
                marca_id=str(query.get("marca_id", "manual")),
                modelo=query["modelo"],
                modelo_id=str(query.get("modelo_id", "manual")),
                ano_modelo=int(query["ano_modelo"]),
                combustivel=query.get("combustivel", ""),
                codigo_fipe=query.get("codigo_fipe", ""),
                valor=Decimal(str(query["valor"])),
                mes_referencia=query.get("mes_referencia", "manual"),
                fonte="manual",
                raw_payload={},
            )
            return Ok(quote)
        except KeyError as e:
            return Err(f"missing_field: {e}")
```

- [ ] **Step 2: Write test for manual**

`tests/unit/integrations/fipe/test_manual.py`:
```python
from decimal import Decimal

import pytest

from app.integrations.fipe.manual import ManualFipeProvider


@pytest.mark.asyncio
async def test_manual_constructs_quote():
    p = ManualFipeProvider()
    r = await p.fetch({
        "action": "price", "tipo": "carro",
        "marca": "Custom", "modelo": "X", "ano_modelo": 2023, "valor": "30000.00",
    })
    assert r.is_ok
    assert r.value.valor == Decimal("30000.00")
    assert r.value.fonte == "manual"


@pytest.mark.asyncio
async def test_manual_missing_field_returns_err():
    p = ManualFipeProvider()
    r = await p.fetch({"action": "price", "tipo": "carro"})
    assert r.is_err
```

- [ ] **Step 3: Write cache layer**

`app/integrations/fipe/cache.py`:
```python
"""Cache layer for FIPE providers using fipe_cache table."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.data.models import FipeCache
from app.integrations.base import Err, Ok, Provider


class CachedFipeProvider:
    """Wraps any FIPE Provider with read-through cache.

    For price queries: TTL in hours (default 24).
    For list queries: TTL in hours (default 720 = 30 days).
    """

    def __init__(
        self,
        wrapped: Provider,
        session_factory,
        listas_ttl_horas: int = 720,
        preco_ttl_horas: int = 24,
    ) -> None:
        self.wrapped = wrapped
        self.session_factory = session_factory
        self.listas_ttl = listas_ttl_horas
        self.preco_ttl = preco_ttl_horas
        self.name = f"cached({wrapped.name})"

    def _key(self, query: dict[str, Any]) -> tuple[str, str | None, str | None, str | None]:
        action = query.get("action", "")
        # Compose a synthetic key per action
        if action == "brands":
            return (f"{query.get('tipo')}/brands", None, None, None)
        if action == "models":
            return (f"{query.get('tipo')}/models", str(query.get("brand_id")), None, None)
        if action == "years":
            return (f"{query.get('tipo')}/years", str(query.get("brand_id")),
                    str(query.get("model_id")), None)
        if action == "price":
            return (f"{query.get('tipo')}/price",
                    str(query.get("brand_id", query.get("codigo_fipe", ""))),
                    str(query.get("model_id", "")),
                    str(query.get("year_id", "")))
        return (action, None, None, None)

    def _ttl(self, query: dict[str, Any]) -> int:
        return self.preco_ttl if query.get("action") == "price" else self.listas_ttl

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        tipo, marca_id, modelo_id, ano_id = self._key(query)
        with self.session_factory() as session:
            stmt = session.query(FipeCache).filter_by(
                tipo=tipo, marca_id=marca_id, modelo_id=modelo_id, ano_id=ano_id,
            )
            row = stmt.first()
            if row is not None:
                age = datetime.utcnow() - row.coletado_em
                if age < timedelta(hours=row.ttl_horas):
                    return Ok(json.loads(row.payload_json))

        result = await self.wrapped.fetch(query)
        if result.is_ok:
            # Serialize VehicleQuote dataclass via dict conversion for cache
            payload = result.value
            if hasattr(payload, "__dataclass_fields__"):
                from dataclasses import asdict
                serialized = json.dumps(asdict(payload), default=str)
            else:
                serialized = json.dumps(payload, default=str)
            with self.session_factory() as session:
                row = FipeCache(
                    tipo=tipo, marca_id=marca_id, modelo_id=modelo_id, ano_id=ano_id,
                    payload_json=serialized, ttl_horas=self._ttl(query),
                )
                session.add(row)
                session.commit()
        return result
```

- [ ] **Step 4: Write test for cache**

`tests/unit/integrations/fipe/test_cache.py`:
```python
import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.integrations.base import Ok
from app.integrations.fipe.cache import CachedFipeProvider


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.calls = 0

    async def fetch(self, query):
        self.calls += 1
        return Ok([{"name": "Acura"}])


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        yield get_session_factory(engine)


@pytest.mark.asyncio
async def test_cache_hits_after_first_call(session_factory):
    inner = FakeProvider()
    cached = CachedFipeProvider(inner, session_factory)
    r1 = await cached.fetch({"action": "brands", "tipo": "carro"})
    r2 = await cached.fetch({"action": "brands", "tipo": "carro"})
    assert r1.is_ok and r2.is_ok
    assert inner.calls == 1  # second call was served from cache
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/integrations/fipe/ -v`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add app/integrations/fipe/manual.py app/integrations/fipe/cache.py tests/unit/integrations/fipe/test_manual.py tests/unit/integrations/fipe/test_cache.py
git commit -m "feat(integrations): FIPE manual provider + cache layer"
```

---

## Task 5: BACEN `IndicatorPoint` schema + SGS provider

**Files:**
- Create: `app/integrations/bacen/__init__.py` (empty)
- Create: `app/integrations/bacen/schema.py`
- Create: `app/integrations/bacen/sgs.py`
- Create: `tests/unit/integrations/bacen/__init__.py`
- Create: `tests/unit/integrations/bacen/test_sgs.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/integrations/bacen/test_sgs.py`:
```python
from datetime import date
from decimal import Decimal

import httpx
import pytest
import respx

from app.integrations.bacen.sgs import BcbSgsProvider


@pytest.mark.asyncio
@respx.mock
async def test_fetch_selic_meta_normalized_to_fraction():
    respx.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados").mock(
        return_value=httpx.Response(200, json=[
            {"data": "23/05/2026", "valor": "10.50"},
        ])
    )
    p = BcbSgsProvider()
    result = await p.fetch({
        "codigo": "SELIC_META",
        "data_inicial": date(2026, 5, 1),
        "data_final": date(2026, 5, 31),
    })
    assert result.is_ok
    points = result.value
    assert len(points) == 1
    # 10.50% -> 0.1050 fraction
    assert points[0].valor_fracao == Decimal("0.1050")
    assert points[0].unidade == "pct_aa"
    assert points[0].fonte == "bcb_sgs"


@pytest.mark.asyncio
@respx.mock
async def test_unknown_codigo_returns_err():
    p = BcbSgsProvider()
    result = await p.fetch({
        "codigo": "INVALID",
        "data_inicial": date(2026, 5, 1),
        "data_final": date(2026, 5, 31),
    })
    assert result.is_err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/integrations/bacen/ -v`
Expected: FAIL.

- [ ] **Step 3: Write schema**

`app/integrations/bacen/schema.py`:
```python
"""BACEN normalized indicator schema."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


Unidade = Literal["pct_aa", "pct_am", "pct_ad"]


@dataclass(frozen=True)
class IndicatorPoint:
    codigo: str
    data_referencia: date
    valor_fracao: Decimal
    unidade: Unidade
    fonte: str
```

- [ ] **Step 4: Write SGS provider**

`app/integrations/bacen/sgs.py`:
```python
"""BACEN SGS primary provider for SELIC, CDI, IPCA, Tx BACEN veiculos."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.bacen.schema import IndicatorPoint, Unidade
from app.integrations.base import Err, Ok


BASE_URL = "https://api.bcb.gov.br/dados/serie"

# (sgs_codigo, unidade)
CODIGOS: dict[str, tuple[int, Unidade]] = {
    "SELIC_META": (432, "pct_aa"),
    "SELIC_DIARIA": (11, "pct_ad"),
    "CDI": (12, "pct_ad"),
    "IPCA": (433, "pct_am"),
    "TX_BACEN_VEIC": (20714, "pct_am"),
}


class BcbSgsProvider:
    name = "bcb_sgs"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=2))
    async def _get_json(self, url: str) -> list[dict[str, Any]]:
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "FinacialSim/0.1"})
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        finally:
            if owned:
                await client.aclose()

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        codigo = query.get("codigo", "")
        if codigo not in CODIGOS:
            return Err(f"unknown_codigo: {codigo}")
        sgs_code, unidade = CODIGOS[codigo]
        di: date = query["data_inicial"]
        df: date = query["data_final"]
        url = (
            f"{BASE_URL}/bcdata.sgs.{sgs_code}/dados"
            f"?formato=json&dataInicial={di.strftime('%d/%m/%Y')}"
            f"&dataFinal={df.strftime('%d/%m/%Y')}"
        )
        try:
            raw = await self._get_json(url)
            points: list[IndicatorPoint] = []
            for entry in raw:
                d_parts = entry["data"].split("/")
                ref_date = date(int(d_parts[2]), int(d_parts[1]), int(d_parts[0]))
                pct = Decimal(entry["valor"])
                # Validate range
                if pct < 0 or pct > 100:
                    return Err(f"invalid_value_out_of_range: {pct}")
                fracao = (pct / Decimal("100")).quantize(Decimal("0.00000001"))
                points.append(IndicatorPoint(
                    codigo=codigo,
                    data_referencia=ref_date,
                    valor_fracao=fracao,
                    unidade=unidade,
                    fonte="bcb_sgs",
                ))
            return Ok(points)
        except httpx.HTTPError as e:
            return Err(f"http_error: {e}")
        except (KeyError, ValueError) as e:
            return Err(f"parse_error: {e}")
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/integrations/bacen/ -v`
Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/integrations/bacen/ tests/unit/integrations/bacen/
git commit -m "feat(integrations): BACEN SGS provider with normalization"
```

---

## Task 6: BACEN BrasilAPI fallback + conversions

**Files:**
- Create: `app/integrations/bacen/brasilapi.py`
- Create: `app/integrations/bacen/conversions.py`
- Create: `tests/unit/integrations/bacen/test_brasilapi.py`
- Create: `tests/unit/integrations/bacen/test_conversions.py`

- [ ] **Step 1: Write `conversions.py`** (pure functions, easy first)

`app/integrations/bacen/conversions.py`:
```python
"""Conversions between rate periodicities."""

from __future__ import annotations

from decimal import Decimal


def mensal_para_anual(taxa_mensal: Decimal) -> Decimal:
    f = float(taxa_mensal)
    return Decimal(str((1.0 + f) ** 12 - 1.0)).quantize(Decimal("0.00000001"))


def anual_para_mensal(taxa_anual: Decimal) -> Decimal:
    f = float(taxa_anual)
    return Decimal(str((1.0 + f) ** (1.0 / 12.0) - 1.0)).quantize(Decimal("0.00000001"))


def diaria_252_para_anual(taxa_diaria: Decimal) -> Decimal:
    f = float(taxa_diaria)
    return Decimal(str((1.0 + f) ** 252 - 1.0)).quantize(Decimal("0.00000001"))


def diaria_252_para_mensal(taxa_diaria: Decimal) -> Decimal:
    f = float(taxa_diaria)
    return Decimal(str((1.0 + f) ** 21 - 1.0)).quantize(Decimal("0.00000001"))
```

- [ ] **Step 2: Test conversions**

`tests/unit/integrations/bacen/test_conversions.py`:
```python
from decimal import Decimal

from app.integrations.bacen.conversions import (
    anual_para_mensal,
    mensal_para_anual,
)


def test_mensal_to_anual_roundtrip():
    m = Decimal("0.015")
    a = mensal_para_anual(m)
    back = anual_para_mensal(a)
    assert abs(back - m) < Decimal("0.000001")


def test_one_pct_mensal_approx_12_68_pct_anual():
    a = mensal_para_anual(Decimal("0.01"))
    # (1.01)^12 - 1 = 0.12683...
    assert abs(a - Decimal("0.12682503")) < Decimal("0.0001")
```

- [ ] **Step 3: Write BrasilAPI fallback**

`app/integrations/bacen/brasilapi.py`:
```python
"""BACEN fallback - BrasilAPI rates endpoint (single latest value)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.bacen.schema import IndicatorPoint
from app.integrations.base import Err, Ok


BASE_URL = "https://brasilapi.com.br/api/taxas/v1"
ALIAS = {"SELIC_META": "Selic", "CDI": "CDI", "IPCA": "IPCA"}


class BrasilApiBacenProvider:
    name = "bacen_brasilapi"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=2))
    async def _get_json(self, url: str) -> Any:
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "FinacialSim/0.1"})
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        finally:
            if owned:
                await client.aclose()

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        codigo = query.get("codigo", "")
        alias = ALIAS.get(codigo)
        if alias is None:
            return Err(f"unsupported_codigo_brasilapi: {codigo}")
        try:
            data = await self._get_json(f"{BASE_URL}/{alias}")
            # BrasilAPI returns { nome, valor } where valor is a percent number
            valor_pct = Decimal(str(data["valor"]))
            if valor_pct < 0 or valor_pct > 100:
                return Err(f"invalid_value: {valor_pct}")
            point = IndicatorPoint(
                codigo=codigo,
                data_referencia=date.today(),
                valor_fracao=(valor_pct / Decimal("100")).quantize(Decimal("0.00000001")),
                unidade="pct_aa" if codigo == "SELIC_META" else "pct_am",
                fonte="brasilapi",
            )
            return Ok([point])
        except httpx.HTTPError as e:
            return Err(f"http_error: {e}")
        except (KeyError, ValueError) as e:
            return Err(f"parse_error: {e}")
```

- [ ] **Step 4: Test BrasilAPI**

`tests/unit/integrations/bacen/test_brasilapi.py`:
```python
from decimal import Decimal

import httpx
import pytest
import respx

from app.integrations.bacen.brasilapi import BrasilApiBacenProvider


@pytest.mark.asyncio
@respx.mock
async def test_brasilapi_selic_returns_point():
    respx.get("https://brasilapi.com.br/api/taxas/v1/Selic").mock(
        return_value=httpx.Response(200, json={"nome": "Selic", "valor": 10.5})
    )
    p = BrasilApiBacenProvider()
    r = await p.fetch({"codigo": "SELIC_META"})
    assert r.is_ok
    assert r.value[0].valor_fracao == Decimal("0.1050")
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/integrations/bacen/ -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add app/integrations/bacen/brasilapi.py app/integrations/bacen/conversions.py tests/unit/integrations/bacen/test_brasilapi.py tests/unit/integrations/bacen/test_conversions.py
git commit -m "feat(integrations): BACEN BrasilAPI fallback + conversions"
```

---

## Task 7: BACEN cache via IndicatorRepository

**Files:**
- Create: `app/integrations/bacen/cached.py`
- Create: `tests/unit/integrations/bacen/test_cached.py`

- [ ] **Step 1: Write `cached.py`** (writes results to `indicators_history` via upsert)

`app/integrations/bacen/cached.py`:
```python
"""BACEN cache layer - persists results to indicators_history."""

from __future__ import annotations

from typing import Any

from app.data.repositories import IndicatorRepository
from app.integrations.base import Err, Ok, Provider


class CachedBacenProvider:
    """Wraps a BACEN Provider; on success, upserts points into indicators_history."""

    def __init__(self, wrapped: Provider, session_factory) -> None:
        self.wrapped = wrapped
        self.session_factory = session_factory
        self.name = f"cached({wrapped.name})"

    async def fetch(self, query: dict[str, Any]) -> Ok[Any] | Err:
        result = await self.wrapped.fetch(query)
        if not result.is_ok:
            return result
        points = result.value
        with self.session_factory() as session:
            repo = IndicatorRepository(session)
            for pt in points:
                repo.upsert(
                    codigo=pt.codigo,
                    data_referencia=pt.data_referencia,
                    valor=pt.valor_fracao,
                    unidade=pt.unidade,
                    fonte=pt.fonte,
                )
        return result
```

- [ ] **Step 2: Test**

`tests/unit/integrations/bacen/test_cached.py`:
```python
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.repositories import IndicatorRepository
from app.integrations.bacen.cached import CachedBacenProvider
from app.integrations.bacen.schema import IndicatorPoint
from app.integrations.base import Ok


class FakeBacen:
    name = "fake"
    async def fetch(self, query):
        return Ok([
            IndicatorPoint(
                codigo="SELIC_META",
                data_referencia=date(2026, 5, 23),
                valor_fracao=Decimal("0.1050"),
                unidade="pct_aa",
                fonte="fake",
            )
        ])


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        yield get_session_factory(engine)


@pytest.mark.asyncio
async def test_cached_writes_to_indicators_history(session_factory):
    cached = CachedBacenProvider(FakeBacen(), session_factory)
    r = await cached.fetch({"codigo": "SELIC_META"})
    assert r.is_ok
    with session_factory() as session:
        repo = IndicatorRepository(session)
        latest = repo.get_latest("SELIC_META")
        assert latest is not None
        assert latest.valor == Decimal("0.10500000")
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/unit/integrations/bacen/ -v`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add app/integrations/bacen/cached.py tests/unit/integrations/bacen/test_cached.py
git commit -m "feat(integrations): BACEN cache layer (persists to indicators_history)"
```

---

## Task 8: Chain composition helpers

**Files:**
- Create: `app/integrations/factory.py`
- Create: `tests/unit/integrations/test_factory.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/integrations/test_factory.py`:
```python
import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.integrations.factory import build_fipe_chain, build_bacen_chain


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        yield get_session_factory(engine)


def test_build_fipe_chain_has_three_providers(session_factory):
    chain = build_fipe_chain(session_factory)
    assert len(chain.providers) == 3


def test_build_bacen_chain_has_two_providers(session_factory):
    chain = build_bacen_chain(session_factory)
    assert len(chain.providers) == 2
```

- [ ] **Step 2: Write factory**

`app/integrations/factory.py`:
```python
"""Composition helpers - build default provider chains."""

from __future__ import annotations

from app.integrations.bacen.brasilapi import BrasilApiBacenProvider
from app.integrations.bacen.cached import CachedBacenProvider
from app.integrations.bacen.sgs import BcbSgsProvider
from app.integrations.base import ProviderChain
from app.integrations.fipe.brasilapi import BrasilApiFipeProvider
from app.integrations.fipe.cache import CachedFipeProvider
from app.integrations.fipe.manual import ManualFipeProvider
from app.integrations.fipe.parallelum import ParallelumFipeProvider


def build_fipe_chain(session_factory, listas_ttl_horas: int = 720, preco_ttl_horas: int = 24) -> ProviderChain:
    parallelum = CachedFipeProvider(
        ParallelumFipeProvider(),
        session_factory,
        listas_ttl_horas=listas_ttl_horas,
        preco_ttl_horas=preco_ttl_horas,
    )
    brasilapi = CachedFipeProvider(
        BrasilApiFipeProvider(),
        session_factory,
        listas_ttl_horas=listas_ttl_horas,
        preco_ttl_horas=preco_ttl_horas,
    )
    manual = ManualFipeProvider()
    return ProviderChain([parallelum, brasilapi, manual])


def build_bacen_chain(session_factory) -> ProviderChain:
    sgs = CachedBacenProvider(BcbSgsProvider(), session_factory)
    brasil = CachedBacenProvider(BrasilApiBacenProvider(), session_factory)
    return ProviderChain([sgs, brasil])
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/unit/integrations/test_factory.py -v`
Expected: 2 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add app/integrations/factory.py tests/unit/integrations/test_factory.py
git commit -m "feat(integrations): default chains factory (FIPE + BACEN)"
```

---

## Task 9: Integration smoke test (real HTTP — marked slow)

**Files:**
- Create: `tests/integration/test_providers_live.py`

- [ ] **Step 1: Write live test (skipped by default)**

`tests/integration/test_providers_live.py`:
```python
"""Smoke tests against real APIs. Disabled by default; run with -m slow."""

from datetime import date

import pytest

from app.integrations.bacen.sgs import BcbSgsProvider
from app.integrations.fipe.parallelum import ParallelumFipeProvider


@pytest.mark.slow
@pytest.mark.asyncio
async def test_parallelum_brands_live():
    p = ParallelumFipeProvider()
    r = await p.fetch({"action": "brands", "tipo": "cars"})
    assert r.is_ok
    assert len(r.value) > 10


@pytest.mark.slow
@pytest.mark.asyncio
async def test_sgs_selic_live():
    p = BcbSgsProvider()
    r = await p.fetch({
        "codigo": "SELIC_META",
        "data_inicial": date(2026, 1, 1),
        "data_final": date.today(),
    })
    assert r.is_ok
    assert len(r.value) >= 1
```

- [ ] **Step 2: Verify mock-only tests still pass**

Run: `pytest tests/unit/integrations/ -v`
Expected: All PASS (live tests skipped because no `-m slow`).

- [ ] **Step 3: Optional — run live**

Run: `pytest tests/integration/test_providers_live.py -v -m slow`
Expected: PASS if internet works; otherwise OK to skip in CI.

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_providers_live.py
git commit -m "test(integrations): live smoke tests for FIPE and BACEN (slow)"
```

---

## Phase 3 — Definition of Done

- [ ] All 9 tasks completed and committed
- [ ] All mock-based tests pass (`pytest tests/unit/integrations/`)
- [ ] Live tests work when internet available (`pytest -m slow`)
- [ ] Cache hits verified for FIPE (second call doesn't increment inner provider counter)
- [ ] BACEN cache writes to `indicators_history` (verified via test_cached)
- [ ] `mypy app/integrations/` passes
- [ ] `ruff check app/integrations/` clean
