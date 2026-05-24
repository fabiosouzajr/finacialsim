from decimal import Decimal

import httpx
import respx

from tests.unit.integrations.conftest import FailingClient
from app.integrations.fipe.brasilapi import BrasilApiFipeProvider


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
    assert result.value[0] == {"id": "1", "nome": "Acura"}


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


async def test_returns_err_on_connect_error():
    p = BrasilApiFipeProvider(client=FailingClient())
    result = await p.fetch({"action": "brands", "tipo": "carro"})
    assert result.is_err
