from datetime import date
from decimal import Decimal

import httpx
import respx

from tests.unit.integrations.conftest import FailingClient
from app.integrations.bacen.sgs import BcbSgsProvider


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
    assert points[0].valor_fracao == Decimal("0.10500000")
    assert points[0].unidade == "pct_aa"
    assert points[0].fonte == "bcb_sgs"


async def test_unknown_codigo_returns_err():
    p = BcbSgsProvider()
    result = await p.fetch({
        "codigo": "INVALID",
        "data_inicial": date(2026, 5, 1),
        "data_final": date(2026, 5, 31),
    })
    assert result.is_err


async def test_returns_err_on_connect_error():
    p = BcbSgsProvider(client=FailingClient())
    result = await p.fetch({
        "codigo": "SELIC_META",
        "data_inicial": date(2026, 5, 1),
        "data_final": date(2026, 5, 31),
    })
    assert result.is_err
