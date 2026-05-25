"""FIPE vehicle price lookup page."""

from __future__ import annotations

from nicegui import ui

from app.data.database import get_session_factory
from app.integrations.factory import build_fipe_chain
from app.ui.layout import shell
from app.utils.br_format import format_brl


def build_fipe_page(engine) -> None:
    SessionLocal = get_session_factory(engine)
    chain = build_fipe_chain(SessionLocal)

    @ui.page("/fipe")
    def page() -> None:
        def content() -> None:
            status = ui.label("Carregando marcas...").classes("text-sm text-gray-500")
            resultado = ui.card().classes("w-full mt-4")

            # Handlers are defined before the selects; Python's late binding means
            # the closure variables (tipo, marca, modelo, ano) are resolved at call
            # time, after all selects have been created.

            async def load_brands(_=None) -> None:
                status.text = "Buscando marcas..."
                r = await chain.fetch({"action": "brands", "tipo": tipo.value})
                if not r.is_ok:
                    ui.notify(f"Erro ao buscar marcas: {r.error}", type="negative")  # type: ignore[union-attr]
                    status.text = ""
                    return
                marca.options = {b["id"]: b["nome"] for b in r.value}  # type: ignore[union-attr]
                marca.value = None
                modelo.options = {}
                modelo.value = None
                ano.options = {}
                ano.value = None
                marca.update()
                resultado.clear()
                status.text = f"{len(r.value)} marcas  •  selecione uma marca"  # type: ignore[union-attr]

            async def load_models(_=None) -> None:
                if not marca.value:
                    return
                status.text = "Buscando modelos..."
                r = await chain.fetch({
                    "action": "models", "tipo": tipo.value, "brand_id": marca.value,
                })
                if not r.is_ok:
                    ui.notify(f"Erro ao buscar modelos: {r.error}", type="negative")  # type: ignore[union-attr]
                    status.text = ""
                    return
                modelo.options = {m["id"]: m["nome"] for m in r.value}  # type: ignore[union-attr]
                modelo.value = None
                ano.options = {}
                ano.value = None
                modelo.update()
                resultado.clear()
                status.text = f"{len(r.value)} modelos  •  selecione um modelo"  # type: ignore[union-attr]

            async def load_years(_=None) -> None:
                if not modelo.value:
                    return
                status.text = "Buscando anos..."
                r = await chain.fetch({
                    "action": "years", "tipo": tipo.value,
                    "brand_id": marca.value, "model_id": modelo.value,
                })
                if not r.is_ok:
                    ui.notify(f"Erro ao buscar anos: {r.error}", type="negative")  # type: ignore[union-attr]
                    status.text = ""
                    return
                ano.options = {y["id"]: y["nome"] for y in r.value}  # type: ignore[union-attr]
                ano.value = None
                ano.update()
                resultado.clear()
                status.text = f"{len(r.value)} anos  •  selecione o ano/combustível"  # type: ignore[union-attr]

            async def get_price(_=None) -> None:
                if not ano.value:
                    return
                status.text = "Buscando preço FIPE..."
                r = await chain.fetch({
                    "action": "price", "tipo": tipo.value,
                    "brand_id": marca.value, "model_id": modelo.value,
                    "year_id": ano.value,
                })
                if not r.is_ok:
                    ui.notify(f"Erro ao buscar preço: {r.error}", type="negative")  # type: ignore[union-attr]
                    status.text = ""
                    return
                q = r.value  # type: ignore[union-attr]
                resultado.clear()
                with resultado:
                    ui.label(f"{q.marca}  {q.modelo}").classes("text-lg font-bold")
                    ui.label(f"Ano modelo: {q.ano_modelo}  •  {q.combustivel}")
                    ui.label(f"Código FIPE: {q.codigo_fipe}")
                    ui.label(format_brl(q.valor)).classes("text-2xl font-bold mt-1")
                    ui.label(
                        f"Referência: {q.mes_referencia}  •  Fonte: {q.fonte}"
                    ).classes("text-sm text-gray-500")
                status.text = "Pronto"

            # Selects created after handlers — on_change constructor param is typed.
            with ui.row().classes("w-full gap-4 items-end flex-wrap"):
                tipo = ui.select(  # pyright: ignore[reportUnusedVariable]
                    ["carro", "moto", "caminhao"], label="Tipo", value="carro",
                    on_change=load_brands,
                ).classes("w-36")
                marca = ui.select({}, label="Marca", on_change=load_models).classes("w-72")  # pyright: ignore[reportUnusedVariable]
                modelo = ui.select({}, label="Modelo", on_change=load_years).classes("w-72")  # pyright: ignore[reportUnusedVariable]
                ano = ui.select({}, label="Ano / Combustível", on_change=get_price).classes("w-44")  # pyright: ignore[reportUnusedVariable]

            # Auto-load brands for the default tipo on page open
            ui.timer(0, load_brands, once=True)

        shell(content)
