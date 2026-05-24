from decimal import Decimal

from app.integrations.fipe.manual import ManualFipeProvider


async def test_manual_constructs_quote():
    p = ManualFipeProvider()
    r = await p.fetch({
        "action": "price", "tipo": "carro",
        "marca": "Custom", "modelo": "X", "ano_modelo": 2023, "valor": "30000.00",
    })
    assert r.is_ok
    assert r.value.valor == Decimal("30000.00")
    assert r.value.fonte == "manual"


async def test_manual_missing_field_returns_err():
    p = ManualFipeProvider()
    r = await p.fetch({"action": "price", "tipo": "carro"})
    assert r.is_err


async def test_manual_invalid_tipo_returns_err():
    p = ManualFipeProvider()
    r = await p.fetch({
        "action": "price", "tipo": "trucks",
        "marca": "X", "modelo": "Y", "ano_modelo": 2020, "valor": "10000",
    })
    assert r.is_err
    assert "invalid_tipo" in r.error


async def test_manual_non_price_action_returns_err():
    p = ManualFipeProvider()
    r = await p.fetch({"action": "brands", "tipo": "carro"})
    assert r.is_err
