from decimal import Decimal

import httpx
import respx

from tests.unit.integrations.conftest import FailingClient
from app.integrations.fipe.parallelum import ParallelumFipeProvider


@respx.mock
async def test_get_brands_for_cars():
    respx.get("https://parallelum.com.br/fipe/api/v2/cars/brands").mock(
        return_value=httpx.Response(200, json=[
            {"code": "1", "name": "Acura"},
            {"code": "2", "name": "Agrale"},
        ])
    )
    p = ParallelumFipeProvider()
    result = await p.fetch({"action": "brands", "tipo": "carro"})
    assert result.is_ok
    brands = result.value
    assert len(brands) == 2
    assert brands[0] == {"id": "1", "nome": "Acura"}


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
        "action": "price", "tipo": "carro",
        "brand_id": "21", "model_id": "1234", "year_id": "2024-1",
    })
    assert result.is_ok
    quote = result.value
    assert quote.valor == Decimal("45230.00")
    assert quote.marca == "Fiat"
    assert quote.codigo_fipe == "001234-5"
    assert quote.fonte == "fipe_parallelum"


async def test_returns_err_on_connect_error():
    p = ParallelumFipeProvider(client=FailingClient())
    result = await p.fetch({"action": "brands", "tipo": "carro"})
    assert result.is_err
    assert "http_error" in result.error
