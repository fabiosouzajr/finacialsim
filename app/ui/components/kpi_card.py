"""KPI card - label + big value + optional secondary text + hide toggle."""

from __future__ import annotations

from nicegui import ui


class KpiCard:
    def __init__(self, label: str, value: str, secondary: str = "") -> None:
        self.visible = True
        with ui.card().classes("kpi-card") as self.card:
            self.label_el = ui.label(label).classes("kpi-label")
            self.value_el = ui.label(value).classes("kpi-value")
            self.secondary_el = ui.label(secondary).classes("kpi-label")
            with ui.row().classes("w-full justify-end"):
                ui.button(icon="visibility", on_click=self._toggle).props("flat dense")

    def _toggle(self) -> None:
        self.visible = not self.visible
        self.value_el.text = "•••" if not self.visible else self.value_el.text
        self.value_el.update()

    def set(self, value: str, secondary: str = "") -> None:
        self.value_el.text = value
        self.secondary_el.text = secondary
        self.value_el.update(); self.secondary_el.update()