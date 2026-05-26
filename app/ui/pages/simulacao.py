"""Simulacao page - the central tab."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

from nicegui import app as ng_app, ui

from app.core.extras import Extra, ExtraModalidade
from app.data.database import get_session_factory
from app.data.models import Vehicle
from app.services.simulation_service import (
    SimulationInputDTO,
    SimulationService,
)
from app.ui.components.charts import (
    composition_chart,
    parcela_total_chart,
    saldo_devedor_chart,
)
from app.ui.components.currency_input import CurrencyInput
from app.ui.components.kpi_card import KpiCard
from app.ui.components.percent_input import PercentInput
from app.ui.layout import shell
from app.ui.router import get_logged_user_id
from app.utils.br_format import format_brl, format_pct
from app.integrations.factory import build_fipe_chain
from app.services.vehicle_service import VehicleService, VehicleServiceError


def build_simulacao_page(engine) -> None:
    SessionLocal = get_session_factory(engine)
    fipe_chain = build_fipe_chain(SessionLocal)

    @ui.page("/simulacao")
    def page() -> None:
        def content() -> None:
            user_id = get_logged_user_id() or 0
            last_sim_id: dict[str, int | None] = {"id": None}
            _actions: dict = {}
            selected_vehicle_id: dict[str, int | None] = {"id": None}

            # ── Header: title left, action buttons right ─────────────────
            with ui.row().classes("w-full items-center justify-between mb-2"):
                ui.label("Simulação").classes("text-xl font-bold text-slate-800")
                with ui.row().classes("gap-2"):
                    ui.button("Simular", icon="play_arrow",
                              on_click=lambda: _actions["simular"]()
                              ).props("color=primary")
                    ui.button("Gerar PDF", icon="picture_as_pdf",
                              on_click=lambda: _actions["gerar_pdf"]()
                              ).props("color=primary outline")

            # ── Main layout: narrow form | wide results ───────────────────
            with ui.row().classes("w-full gap-4 items-start"):

                # ── Left: Entrada form ────────────────────────────────────
                with ui.column().classes("gap-3").style("width: 290px; flex-shrink: 0"):
                    ui.label("Entrada").classes(
                        "text-xs font-semibold text-slate-500 uppercase tracking-widest"
                    )

                    # ── Seção Veículo ─────────────────────────────────────────
                    ui.label("Veículo").classes(
                        "text-xs font-semibold text-slate-500 uppercase tracking-widest"
                    )

                    picker_row = ui.column().classes("w-full gap-1")
                    chips_row = ui.row().classes("gap-2 flex-wrap")
                    chips_row.set_visibility(False)
                    fipe_panel = ui.column().classes("w-full gap-2")
                    fipe_panel.set_visibility(False)

                    def _build_picker() -> None:
                        picker_row.clear()
                        with SessionLocal() as _s:
                            opts = VehicleService(_s).list_active()
                        options = {
                            v.id: (
                                f"{v.marca} {v.modelo} {v.ano_modelo}"
                                + (f" · {v.placa}" if v.placa else "")
                                + (f" · {v.cor}" if v.cor else "")
                            )
                            for v in opts
                        }
                        options[0] = "— sem veículo —"
                        with picker_row:
                            ui.select(
                                options, value=selected_vehicle_id["id"] or 0,
                                label="Veículo do estoque",
                                on_change=lambda e: _on_picker_change(e.value),
                            ).classes("w-full")

                    def _on_picker_change(vid: int) -> None:
                        if vid == 0:
                            selected_vehicle_id["id"] = None
                            chips_row.set_visibility(False)
                            return
                        selected_vehicle_id["id"] = vid
                        _show_chips(vid)

                    def _show_chips(vid: int) -> None:
                        chips_row.clear()
                        with SessionLocal() as _s:
                            from app.data.models import Vehicle as _V
                            v = _s.get(_V, vid)
                            if v is None:
                                return
                            vf = v.valor_fipe
                            vr = v.valor_referencia
                        chips_row.set_visibility(True)
                        with chips_row:
                            if vf:
                                ui.button(
                                    f"FIPE  {format_brl(vf)}",
                                    on_click=lambda vf=vf: _set_valor_veiculo(vf),
                                ).props("outline dense no-caps color=positive size=sm")
                            ui.button(
                                f"Ref.  {format_brl(vr)}",
                                on_click=lambda vr=vr: _set_valor_veiculo(vr),
                            ).props("outline dense no-caps color=primary size=sm")

                    def _set_valor_veiculo(val: Decimal) -> None:
                        valor_veiculo.value = val

                    _build_picker()

                    ui.button(
                        "🔍 Buscar na FIPE e cadastrar",
                        on_click=lambda: ui.timer(0, _toggle_fipe_panel, once=True),
                    ).props("flat dense no-caps size=sm").classes("text-blue-600 text-xs self-start")

                    async def _toggle_fipe_panel() -> None:
                        visible = not fipe_panel.visible
                        fipe_panel.set_visibility(visible)
                        if visible:
                            await _load_brands_sim()

                    with fipe_panel:
                        sim_fipe_status = ui.label("").classes("text-xs text-slate-400")
                        sim_quote: dict = {"q": None}

                        async def _load_brands_sim(_=None) -> None:
                            sim_fipe_status.text = "Buscando marcas..."
                            r = await fipe_chain.fetch({"action": "brands", "tipo": sim_tipo.value})
                            if not r.is_ok:
                                ui.notify(f"Erro: {r.error}", type="negative")
                                return
                            sim_marca.options = {b["id"]: b["nome"] for b in r.value}
                            sim_marca.value = None
                            sim_modelo.options = {}
                            sim_modelo.value = None
                            sim_ano.options = {}
                            sim_ano.value = None
                            sim_quote["q"] = None
                            sim_result_box.set_visibility(False)
                            sim_marca.update()
                            sim_fipe_status.text = f"{len(r.value)} marcas"

                        async def _load_models_sim(_=None) -> None:
                            if not sim_marca.value:
                                return
                            r = await fipe_chain.fetch({
                                "action": "models", "tipo": sim_tipo.value,
                                "brand_id": sim_marca.value,
                            })
                            if not r.is_ok:
                                return
                            sim_modelo.options = {m["id"]: m["nome"] for m in r.value}
                            sim_modelo.value = None
                            sim_ano.options = {}
                            sim_ano.value = None
                            sim_modelo.update()

                        async def _load_years_sim(_=None) -> None:
                            if not sim_modelo.value:
                                return
                            r = await fipe_chain.fetch({
                                "action": "years", "tipo": sim_tipo.value,
                                "brand_id": sim_marca.value, "model_id": sim_modelo.value,
                            })
                            if not r.is_ok:
                                return
                            sim_ano.options = {y["id"]: y["nome"] for y in r.value}
                            sim_ano.value = None
                            sim_ano.update()

                        async def _get_price_sim(_=None) -> None:
                            if not sim_ano.value:
                                return
                            r = await fipe_chain.fetch({
                                "action": "price", "tipo": sim_tipo.value,
                                "brand_id": sim_marca.value, "model_id": sim_modelo.value,
                                "year_id": sim_ano.value,
                            })
                            if not r.is_ok:
                                return
                            sim_quote["q"] = r.value
                            q = r.value
                            sim_result_box.set_visibility(True)
                            sim_result_label.text = (
                                f"{q.marca} {q.modelo} {q.ano_modelo} · {format_brl(q.valor)}"
                            )
                            sim_ref_inp.value = q.valor

                        sim_tipo = ui.select(
                            ["carro", "moto", "caminhao"], label="Tipo", value="carro",
                            on_change=_load_brands_sim,
                        ).classes("w-full")
                        sim_marca = ui.select({}, label="Marca", on_change=_load_models_sim).classes("w-full")
                        sim_modelo = ui.select({}, label="Modelo", on_change=_load_years_sim).classes("w-full")
                        sim_ano = ui.select({}, label="Ano", on_change=_get_price_sim).classes("w-full")

                        with ui.column().classes("w-full gap-2") as sim_result_box:
                            sim_result_box.set_visibility(False)
                            sim_result_label = ui.label("").classes("text-xs font-medium text-slate-700")
                            sim_cor_inp = ui.input(label="Cor").classes("w-full")
                            sim_placa_inp = ui.input(label="Placa").classes("w-full")
                            sim_km_inp = ui.number(label="Odômetro (km)", min=0).classes("w-full")
                            sim_ref_inp = CurrencyInput("Valor de referência (R$)", Decimal("0"))

                            def _cadastrar_e_usar() -> None:
                                q = sim_quote["q"]
                                if q is None:
                                    return
                                with SessionLocal() as session:
                                    svc = VehicleService(session)
                                    try:
                                        v = svc.create_from_fipe(
                                            quote=q,
                                            cor=sim_cor_inp.value or None,
                                            placa=sim_placa_inp.value or None,
                                            odometro_km=int(sim_km_inp.value) if sim_km_inp.value else None,
                                            valor_referencia=sim_ref_inp.value,
                                            criado_por=user_id,
                                        )
                                        selected_vehicle_id["id"] = v.id
                                        valor_veiculo.value = v.valor_referencia
                                        fipe_panel.set_visibility(False)
                                        _build_picker()
                                        _show_chips(v.id)
                                        ui.notify("Veículo cadastrado e selecionado!", type="positive")
                                    except VehicleServiceError as e:
                                        ui.notify(str(e), type="negative")

                            ui.button("+ Cadastrar e usar este veículo",
                                      on_click=_cadastrar_e_usar).props("color=primary").classes("w-full")

                    ui.separator().classes("my-1")
                    # ── fim seção Veículo ─────────────────────────────────────

                    valor_veiculo = CurrencyInput("Valor do veículo", Decimal("50000"))
                    valor_entrada = CurrencyInput("Entrada (R$)", Decimal("10000"))
                    prazo = ui.number(label="Prazo (meses)", value=48, min=12, max=72).classes("w-full")
                    taxa = PercentInput("Taxa mensal", Decimal("0.0189"))
                    incluir_iof = ui.checkbox("Incluir IOF", value=True)

                    # Custos adicionais above calendars
                    with ui.expansion("Custos adicionais").classes("w-full"):
                        protecao = CurrencyInput("Proteção veicular (R$/mês)", Decimal("0"))
                        ipva_total = CurrencyInput("IPVA anual (R$)", Decimal("0"))
                        empl_total = CurrencyInput("Emplacamento anual (R$)", Decimal("0"))

                    # Date pickers side by side (popup style)
                    ui.label("Datas").classes(
                        "text-xs font-semibold text-slate-500 uppercase tracking-widest mt-1"
                    )
                    with ui.row().classes("gap-2 w-full"):
                        with ui.column().classes("flex-1 gap-1"):
                            ui.label("Início").classes("text-xs text-slate-400 font-medium")
                            with ui.input(value=date.today().isoformat()).classes("w-full") as inp_lib:
                                with inp_lib.add_slot("append"):
                                    ui.icon("edit_calendar").on(
                                        "click", lambda: menu_lib.open()
                                    ).classes("cursor-pointer text-slate-400")
                                with ui.menu() as menu_lib:
                                    _lib_date = ui.date(
                                        mask="YYYY-MM-DD", value=date.today().isoformat()
                                    )
                                    _lib_date.bind_value(inp_lib)

                        with ui.column().classes("flex-1 gap-1"):
                            _venc_def = (date.today() + timedelta(days=30)).isoformat()
                            ui.label("Término").classes("text-xs text-slate-400 font-medium")
                            with ui.input(value=_venc_def).classes("w-full") as inp_venc:
                                with inp_venc.add_slot("append"):
                                    ui.icon("edit_calendar").on(
                                        "click", lambda: menu_venc.open()
                                    ).classes("cursor-pointer text-slate-400")
                                with ui.menu() as menu_venc:
                                    _venc_date = ui.date(mask="YYYY-MM-DD", value=_venc_def)
                                    _venc_date.bind_value(inp_venc)

                # ── Right: Resultado KPIs + Charts ────────────────────────
                with ui.column().classes("flex-1 gap-3 min-w-0"):

                    # KPI cards — grouped, compact
                    ui.label("Resultado").classes(
                        "text-xs font-semibold text-slate-500 uppercase tracking-widest"
                    )

                    ui.label("Parcelas").classes("kpi-group-label")
                    with ui.row().classes("gap-2 w-full"):
                        with ui.element("div").classes("flex-1"):
                            card_parcela = KpiCard("Parcela financiamento", "R$ 0,00", compact=True)
                        with ui.element("div").classes("flex-1"):
                            card_total_apos = KpiCard("Valor da parcela", "R$ 0,00", compact=True)

                    ui.label("Financiamento").classes("kpi-group-label mt-1")
                    with ui.row().classes("gap-2 w-full"):
                        with ui.element("div").classes("flex-1"):
                            card_financiado = KpiCard("Valor financiado", "R$ 0,00", compact=True)
                        with ui.element("div").classes("flex-1"):
                            card_total_pago = KpiCard("Total pago", "R$ 0,00", compact=True)
                        with ui.element("div").classes("flex-1"):
                            card_cet = KpiCard("CET", "0,00% a.m.", compact=True)

                    # Charts — composition + saldo side by side, parcela_total full width
                    with ui.row().classes("gap-2 w-full"):
                        chart_comp = ui.plotly(composition_chart([], [], [])).classes("flex-1")
                        chart_saldo = ui.plotly(saldo_devedor_chart([])).classes("flex-1")
                    chart_total = ui.plotly(parcela_total_chart([])).classes("w-full")

            # ── Callbacks (bound after UI built via _actions) ─────────────
            def simular() -> None:
                with SessionLocal() as session:
                    if selected_vehicle_id["id"]:
                        v = session.get(Vehicle, selected_vehicle_id["id"])
                        if v is None:
                            ui.notify("Veículo selecionado não encontrado.", type="negative")
                            return
                    else:
                        v = Vehicle(
                            fonte="manual", tipo="carro", marca="Manual", modelo="Veiculo",
                            ano_modelo=date.today().year, combustivel="Gasolina",
                            valor_referencia=valor_veiculo.value,
                        )
                        session.add(v)
                        session.commit()

                    extras = []
                    prazo_int = int(prazo.value or 48)
                    num_anos = math.ceil(prazo_int / 12)
                    if protecao.value > 0:
                        extras.append(Extra("protecao_veicular", "Plano de protecao",
                                            protecao.value, ExtraModalidade.MENSAL_CONTINUO,
                                            prazo_int, 1))
                    if ipva_total.value > 0:
                        extras.append(Extra("ipva", "IPVA", ipva_total.value * num_anos,
                                            ExtraModalidade.RATEIO_MESES,
                                            prazo_int, 2))
                    if empl_total.value > 0:
                        extras.append(Extra("emplacamento", "Emplacamento", empl_total.value * num_anos,
                                            ExtraModalidade.RATEIO_MESES,
                                            prazo_int, 3))

                    sim = SimulationService(session).run_and_save(SimulationInputDTO(
                        criado_por=user_id, cliente_id=None, veiculo_id=v.id,
                        valor_veiculo=valor_veiculo.value, valor_entrada=valor_entrada.value,
                        prazo_meses=prazo_int, taxa_mensal=taxa.value,
                        data_liberacao=date.fromisoformat(inp_lib.value or date.today().isoformat()),
                        data_primeiro_venc=date.fromisoformat(
                            inp_venc.value or (date.today() + timedelta(days=30)).isoformat()
                        ),
                        incluir_iof=bool(incluir_iof.value), tarifas=[], extras=extras,
                    ))
                    last_sim_id["id"] = sim.id

                    from app.data.models import AmortizationRow
                    rows = (
                        session.query(AmortizationRow).filter_by(simulation_id=sim.id)
                        .order_by(AmortizationRow.numero_parcela).all()
                    )

                card_parcela.set(format_brl(sim.valor_parcela))
                if rows:
                    last_idx = min(12, len(rows) - 1)
                    card_total_apos.set(format_brl(rows[last_idx].parcela_total))
                card_financiado.set(format_brl(sim.valor_financiado))
                total_pago_cliente = (
                    sum((Decimal(str(r.parcela_total)) for r in rows), start=Decimal("0"))
                    + valor_entrada.value
                )
                card_total_pago.set(format_brl(total_pago_cliente))
                card_cet.set(f"{format_pct(sim.cet_mes)} a.m.", f"{format_pct(sim.cet_ano)} a.a.")

                juros = [Decimal(str(r.juros)) for r in rows]
                amort = [Decimal(str(r.amortizacao)) for r in rows]
                extras_arr = [Decimal(str(r.extras_total)) for r in rows]
                saldos = [Decimal(str(r.saldo_devedor)) for r in rows]
                totals = [Decimal(str(r.parcela_total)) for r in rows]
                chart_comp.update_figure(composition_chart(juros, amort, extras_arr))
                chart_saldo.update_figure(saldo_devedor_chart(saldos))
                chart_total.update_figure(parcela_total_chart(totals))

            def gerar_pdf() -> None:
                if last_sim_id["id"] is None:
                    ui.notify("Simule antes de gerar PDF", type="warning")
                    return
                from app.main import _platform_data_dir
                from app.ui.pages._proposal_helper import generate_and_open_pdf
                try:
                    with SessionLocal() as session:
                        generate_and_open_pdf(session, last_sim_id["id"], user_id, _platform_data_dir())
                except Exception as exc:
                    ui.notify(f"Erro ao gerar PDF: {exc}", type="negative")

            _actions["simular"] = simular
            _actions["gerar_pdf"] = gerar_pdf

        shell(content)
