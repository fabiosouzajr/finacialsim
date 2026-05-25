"""Indicadores economicos page."""

from __future__ import annotations

from nicegui import ui

from app.data.database import get_session_factory
from app.data.repositories import IndicatorRepository
from app.ui.components.kpi_card import KpiCard
from app.ui.layout import shell
from app.utils.br_format import format_date_br, format_pct


CODIGOS = ["SELIC_META", "CDI", "IPCA", "TX_BACEN_VEIC"]


def build_indicadores_page(engine) -> None:
    SessionLocal = get_session_factory(engine)

    @ui.page("/indicadores")
    def page() -> None:
        def content() -> None:
            with ui.row().classes("w-full gap-4"):
                with SessionLocal() as session:
                    repo = IndicatorRepository(session)
                    for codigo in CODIGOS:
                        row = repo.get_latest(codigo)
                        if row:
                            KpiCard(codigo, format_pct(row.valor),
                                    f"em {format_date_br(row.data_referencia)} ({row.fonte})")
                        else:
                            KpiCard(codigo, "n/d", "sem coleta")

        shell(content)