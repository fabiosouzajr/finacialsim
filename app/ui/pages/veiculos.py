# app/ui/pages/veiculos.py
"""Vehicle registry page."""
from __future__ import annotations

from nicegui import ui

from app.data.database import get_session_factory
from app.integrations.factory import build_fipe_chain
from app.services.vehicle_service import VehicleService
from app.ui.layout import shell
from app.ui.router import get_logged_user_id


def build_veiculos_page(engine) -> None:
    SessionLocal = get_session_factory(engine)
    chain = build_fipe_chain(SessionLocal)

    @ui.page("/veiculos")
    def page() -> None:
        def content() -> None:
            ui.label("Veículos").classes("text-xl font-bold text-slate-800")
            ui.label("Em construção").classes("text-slate-400")

        shell(content)
