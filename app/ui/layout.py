"""Common layout - topbar + tabs nav. Used by all pages except /login."""

from __future__ import annotations

from typing import Callable

from nicegui import app, ui

from app.ui.router import get_logged_perfil, logout, navigate


# (label, route, allowed_roles)
TABS = [
    ("Dashboard", "/dashboard", {"vendedor", "gerente", "admin"}),
    ("Cadastro", "/cadastro", {"vendedor", "gerente", "admin"}),
    ("Simulacao", "/simulacao", {"vendedor", "gerente", "admin"}),
    ("Comparativo", "/comparativo", {"vendedor", "gerente", "admin"}),
    ("Amortizacao", "/amortizacao", {"vendedor", "gerente", "admin"}),
    ("Indicadores", "/indicadores", {"vendedor", "gerente", "admin"}),
    ("Configuracoes", "/configuracoes", {"admin"}),
    ("APIs", "/apis", {"gerente", "admin"}),
    ("Logs", "/logs", {"gerente", "admin"}),
    ("Documentacao", "/docs", {"vendedor", "gerente", "admin"}),
]


def shell(content_builder: Callable[[], None]) -> None:
    perfil = get_logged_perfil()
    nome = app.storage.user.get("nome", "")

    with ui.header().classes("bg-primary text-white items-center"):
        ui.label("FinacialSim").classes("text-lg font-bold mr-4")
        with ui.row().classes("ml-auto items-center"):
            ui.label(f"{nome} ({perfil})")
            ui.button(icon="logout", on_click=_do_logout).props("flat dense")

    with ui.tabs().classes("w-full") as tabs_ui:
        for label, route, roles in TABS:
            if perfil in roles:
                ui.tab(name=route, label=label).on(
                    "click", lambda r=route: navigate(r)
                )

    with ui.row().classes("w-full p-4"):
        content_builder()


def _do_logout() -> None:
    logout()
    navigate("/login")