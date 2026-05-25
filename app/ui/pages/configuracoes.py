"""Configuracoes - edit business_rules."""

from __future__ import annotations

from nicegui import ui

from app.data.database import get_session_factory
from app.services.rules_service import RulesService
from app.ui.layout import shell
from app.ui.router import get_logged_user_id


EDITABLE_KEYS = [
    "entrada_minima_pct", "prazo_minimo_meses", "prazo_maximo_meses",
    "taxa_minima_mes", "taxa_maxima_mes", "dias_max_carencia",
    "valor_minimo_financiado", "incluir_iof_default",
    "iof_fixo_pct", "iof_diario_pct", "iof_diario_max_dias",
    "rateio_ipva_meses_default", "rateio_emplacamento_meses_default",
    "backup_diario_horario", "update_indicadores_horario",
    "fipe_cache_listas_ttl_dias", "fipe_cache_preco_ttl_horas",
]


def build_configuracoes_page(engine) -> None:
    SessionLocal = get_session_factory(engine)

    @ui.page("/configuracoes")
    def page() -> None:
        def content() -> None:
            ui.label("Regras de negocio").classes("text-lg font-bold")
            inputs: dict[str, ui.input] = {}
            with SessionLocal() as session:
                svc = RulesService(session)
                for k in EDITABLE_KEYS:
                    raw = svc.get_raw(k) or ""
                    inputs[k] = ui.input(label=k, value=raw)

            def save_all() -> None:
                user_id = get_logged_user_id()
                with SessionLocal() as session:
                    svc = RulesService(session)
                    for k, inp in inputs.items():
                        svc.set(k, inp.value, user_id=user_id)
                ui.notify("Configuracoes salvas", type="positive")

            ui.button("Salvar tudo", on_click=save_all).classes("mt-4")

        shell(content)