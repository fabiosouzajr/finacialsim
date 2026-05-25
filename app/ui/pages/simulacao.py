"""Simulacao page - the central tab."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from nicegui import ui

from app.core.extras import Extra, ExtraModalidade
from app.data.database import get_session_factory
from app.data.models import Vehicle
from app.services.simulation_service import (
    SimulationInputDTO,
    SimulationService,
    Tarifa,
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


def build_simulacao_page(engine) -> None:
    SessionLocal = get_session_factory(engine)

    @ui.page("/simulacao")
    def page() -> None:
        def content() -> None:
            user_id = get_logged_user_id() or 0
            last_sim_id: dict[str, int | None] = {"id": None}

            with ui.row().classes("w-full"):
                with ui.column().classes("w-1/3"):
                    ui.label("Entrada").classes("text-lg font-bold")
                    valor_veiculo = CurrencyInput("Valor do veiculo", Decimal("50000"))
                    valor_entrada = CurrencyInput("Entrada (R$)", Decimal("10000"))
                    prazo = ui.number(label="Prazo (meses)", value=48, min=12, max=72)
                    taxa = PercentInput("Taxa mensal", Decimal("0.0189"))
                    data_lib = ui.date(value=date.today().isoformat())
                    data_venc = ui.date(value=(date.today() + timedelta(days=30)).isoformat())
                    incluir_iof = ui.checkbox("Incluir IOF", value=True)

                    with ui.expansion("Custos adicionais mensais"):
                        protecao = CurrencyInput("Plano de protecao (R$/mes)", Decimal("0"))
                        ipva_total = CurrencyInput("IPVA anual (R$)", Decimal("0"))
                        empl_total = CurrencyInput("Emplacamento (R$ total)", Decimal("0"))
                        rateio = ui.number(label="Rateio (meses)", value=12, min=1, max=72)

                with ui.column().classes("w-1/3"):
                    ui.label("Resultado").classes("text-lg font-bold")
                    card_parcela = KpiCard("Parcela financiamento", "R$ 0,00")
                    card_total_1ano = KpiCard("Parcela total (1o ano)", "R$ 0,00")
                    card_total_apos = KpiCard("Parcela total (apos rateio)", "R$ 0,00")
                    card_financiado = KpiCard("Valor financiado", "R$ 0,00")
                    card_total_pago = KpiCard("Total pago financiamento", "R$ 0,00")
                    card_cet = KpiCard("CET", "0,00% a.m.")

                with ui.column().classes("w-1/3"):
                    chart_comp = ui.plotly(composition_chart([], [], []))
                    chart_saldo = ui.plotly(saldo_devedor_chart([]))
                    chart_total = ui.plotly(parcela_total_chart([]))

            def simular() -> None:
                with SessionLocal() as session:
                    v = Vehicle(
                        fonte="manual", tipo="carro", marca="Manual", modelo="Veiculo",
                        ano_modelo=date.today().year, combustivel="Gasolina",
                        valor_referencia=valor_veiculo.value,
                    )
                    session.add(v); session.commit()

                    extras = []
                    if protecao.value > 0:
                        extras.append(Extra("protecao_veicular", "Plano de protecao",
                                            protecao.value, ExtraModalidade.MENSAL_CONTINUO,
                                            int(prazo.value), 1))
                    if ipva_total.value > 0:
                        extras.append(Extra("ipva", "IPVA", ipva_total.value,
                                            ExtraModalidade.RATEIO_MESES,
                                            int(rateio.value), 2))
                    if empl_total.value > 0:
                        extras.append(Extra("emplacamento", "Emplacamento", empl_total.value,
                                            ExtraModalidade.RATEIO_MESES,
                                            int(rateio.value), 3))

                    sim = SimulationService(session).run_and_save(SimulationInputDTO(
                        criado_por=user_id, cliente_id=None, veiculo_id=v.id,
                        valor_veiculo=valor_veiculo.value, valor_entrada=valor_entrada.value,
                        prazo_meses=int(prazo.value), taxa_mensal=taxa.value,
                        data_liberacao=date.fromisoformat(data_lib.value),
                        data_primeiro_venc=date.fromisoformat(data_venc.value),
                        incluir_iof=incluir_iof.value, tarifas=[], extras=extras,
                    ))
                    last_sim_id["id"] = sim.id

                    from app.data.models import AmortizationRow
                    rows = (
                        session.query(AmortizationRow).filter_by(simulation_id=sim.id)
                        .order_by(AmortizationRow.numero_parcela).all()
                    )

                # Update KPIs
                card_parcela.set(format_brl(sim.valor_parcela))
                if rows:
                    card_total_1ano.set(format_brl(rows[0].parcela_total))
                    last_idx = min(12, len(rows) - 1)
                    card_total_apos.set(format_brl(rows[last_idx].parcela_total))
                card_financiado.set(format_brl(sim.valor_financiado))
                card_total_pago.set(format_brl(sim.total_pago))
                card_cet.set(f"{format_pct(sim.cet_mes)} a.m.", f"{format_pct(sim.cet_ano)} a.a.")

                # Update charts
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

            ui.button("Simular", on_click=simular).classes("mt-4")
            ui.button("Gerar PDF", on_click=gerar_pdf).classes("ml-2")

        shell(content)