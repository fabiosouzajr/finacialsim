from datetime import date
from decimal import Decimal

from app.data.models import (
    AppSetting,
    AuditLog,
    BusinessRule,
    FipeCache,
    IndicatorHistory,
)


def test_business_rule_unique_chave(session) -> None:
    r = BusinessRule(chave="entrada_minima_pct", valor_json="0.10", descricao="10%")
    session.add(r)
    session.commit()
    assert r.id is not None


def test_indicator_history_unique_codigo_data(session) -> None:
    i = IndicatorHistory(
        codigo="SELIC", data_referencia=date(2026, 5, 23),
        valor=Decimal("0.1050"), unidade="pct_aa", fonte="bcb_sgs",
    )
    session.add(i)
    session.commit()
    assert i.id is not None


def test_audit_log(session) -> None:
    from app.data.models import _utcnow
    log = AuditLog(timestamp=_utcnow(), acao="login")
    session.add(log)
    session.commit()
    assert log.id is not None


def test_app_setting(session) -> None:
    s = AppSetting(chave="theme", valor_json='"light"')
    session.add(s)
    session.commit()
    assert s.chave == "theme"


def test_fipe_cache(session) -> None:
    f = FipeCache(tipo="cars", marca_id="m1", modelo_id="mo1", ano_id="a1",
                  payload_json="{}", ttl_horas=720)
    session.add(f)
    session.commit()
    assert f.id is not None
