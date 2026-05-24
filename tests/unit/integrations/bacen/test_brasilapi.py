from decimal import Decimal

import httpx
import respx

from tests.unit.integrations.conftest import FailingClient
from app.integrations.bacen.brasilapi import BrasilApiBacenProvider


@respx.mock
async def test_brasilapi_selic_returns_point():
    respx.get("https://brasilapi.com.br/api/taxas/v1/Selic").mock(
        return_value=httpx.Response(200, json={"nome": "Selic", "valor": 10.5})
    )
    p = BrasilApiBacenProvider()
    r = await p.fetch({"codigo": "SELIC_META"})
    assert r.is_ok
    assert r.value[0].valor_fracao == Decimal("0.10500000")


async def test_returns_err_on_connect_error():
    p = BrasilApiBacenProvider(client=FailingClient())
    r = await p.fetch({"codigo": "SELIC_META"})
    assert r.is_err
