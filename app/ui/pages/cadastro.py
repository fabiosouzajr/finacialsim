"""Cadastro page - clientes + usuarios sub-tabs."""

from __future__ import annotations

from nicegui import ui

from app.data.database import get_session_factory
from app.services.auth_service import AuthError, AuthService
from app.services.client_service import ClientService, ClientServiceError
from app.ui.layout import shell
from app.ui.router import get_logged_perfil, get_logged_user_id


def build_cadastro_page(engine) -> None:
    SessionLocal = get_session_factory(engine)

    @ui.page("/cadastro")
    def page() -> None:
        def content() -> None:
            perfil = get_logged_perfil()
            current_user = get_logged_user_id() or 0
            with ui.tabs() as inner_tabs:
                cli_tab = ui.tab("Clientes")
                if perfil == "admin":
                    usr_tab = ui.tab("Usuarios")
            with ui.tab_panels(inner_tabs, value=cli_tab).classes("w-full"):
                with ui.tab_panel(cli_tab):
                    _clients_panel(SessionLocal, current_user)
                if perfil == "admin":
                    with ui.tab_panel(usr_tab):
                        _users_panel(SessionLocal)

        shell(content)


def _clients_panel(SessionLocal, user_id: int) -> None:
    nome = ui.input("Nome")
    tipo = ui.select(["PF", "PJ"], value="PF", label="Tipo")
    cpf = ui.input("CPF/CNPJ")
    telefone = ui.input("Telefone")
    email = ui.input("Email")
    status = ui.label("").classes("text-sm")

    def save() -> None:
        with SessionLocal() as session:
            svc = ClientService(session)
            try:
                if tipo.value == "PF":
                    svc.create_pf(nome=nome.value, cpf=cpf.value, criado_por=user_id,
                                  telefone=telefone.value, email=email.value)
                else:
                    svc.create_pj(razao_social=nome.value, cnpj=cpf.value, criado_por=user_id,
                                  telefone=telefone.value, email=email.value)
                status.text = "Cliente cadastrado com sucesso"
                status.classes("text-green-600")
                status.update()
                _refresh_client_list(SessionLocal, table_data)
            except ClientServiceError as e:
                status.text = str(e); status.classes("text-red-600"); status.update()

    ui.button("Cadastrar", on_click=save)

    table_data: list[dict] = []
    ui.label("Clientes cadastrados").classes("text-lg mt-4")
    table = ui.table(
        columns=[
            {"name": "nome", "label": "Nome", "field": "nome"},
            {"name": "doc", "label": "CPF/CNPJ", "field": "doc"},
            {"name": "tipo", "label": "Tipo", "field": "tipo"},
            {"name": "telefone", "label": "Telefone", "field": "telefone"},
        ],
        rows=table_data,
    )

    def _refresh_client_list(SessionLocal, data):
        with SessionLocal() as session:
            results = ClientService(session).find("")
            data.clear()
            data.extend([
                {"nome": c.nome, "doc": c.cpf_cnpj, "tipo": c.tipo, "telefone": c.telefone}
                for c in results
            ])
            table.update()

    _refresh_client_list(SessionLocal, table_data)


def _users_panel(SessionLocal) -> None:
    nome = ui.input("Nome")
    pin = ui.input("PIN (4-6 digitos)", password=True)
    perfil = ui.select(["vendedor", "gerente", "admin"], value="vendedor", label="Perfil")
    status = ui.label("").classes("text-sm")

    def save() -> None:
        with SessionLocal() as session:
            try:
                AuthService(session).create_user(nome=nome.value, pin=pin.value, perfil=perfil.value)
                status.text = "Usuario criado"; status.classes("text-green-600"); status.update()
            except AuthError as e:
                status.text = str(e); status.classes("text-red-600"); status.update()

    ui.button("Criar usuario", on_click=save)