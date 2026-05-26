# Design Spec — Simulacao Smart Defaults

**Date:** 2026-05-26
**Status:** Approved
**File scope:** `app/ui/pages/simulacao.py` only

---

## Overview

Three UX improvements to the Simulacao form:
1. **Cliente selector** — searchable dropdown to associate a client with the simulation.
2. **Entrada smart default** — pre-filled from `entrada_minima_pct x valor_veiculo`; live % indicator with amber warning when below minimum.
3. **Taxa mensal from BACEN** — pre-filled from `TX_BACEN_VEIC` indicator; auto-updates reactively while the page is open.

No new models, no migrations, no new services.

---

## Data Loading

At the start of `content()`, before any UI is built, one synchronous DB session reads all page data:

```python
with SessionLocal() as session:
    entrada_minima_pct = Decimal(
        RulesService(session).get_raw("entrada_minima_pct") or "0.10"
    )
    taxa_bacen_row = IndicatorRepository(session).get_latest("TX_BACEN_VEIC")
    taxa_bacen_val = taxa_bacen_row.valor if taxa_bacen_row else None
    clients = ClientService(session).find("")
```

Session closes immediately. All subsequent DB access (simular, nova_a_partir, etc.) uses existing per-callback session patterns unchanged.

**New imports to add to `simulacao.py`:**
- `from app.data.repositories import IndicatorRepository`
- `from app.services.client_service import ClientService`
- `from app.services.rules_service import RulesService`

---

## Feature 1: Cliente Selector

### Placement
Top of the left form column, above the existing "Veiculo" section label.

### Section label
```
"Cliente"  — styled: text-xs font-semibold text-slate-500 uppercase tracking-widest
```

### Widget
```python
cliente_options = {None: "— sem cliente —"}
cliente_options.update({c.id: f"{c.nome}  ({c.cpf_cnpj})" for c in clients})

cliente_sel = ui.select(
    cliente_options,
    value=None,
    label="Cliente",
    with_input=True,
    clearable=True,
).classes("w-full")
```

- `with_input=True` enables built-in client-side search filter.
- Default: `None` ("— sem cliente —"). Selection is optional.
- Clearable: clicking x resets to `None`.

### DTO wiring
`SimulationInputDTO.cliente_id` is already `int | None`. The `simular()` callback passes `cliente_id=cliente_sel.value`. No service-layer changes needed.

---

## Feature 2: Entrada Pre-fill + % Indicator

### Pre-fill
`valor_entrada` is initialized at page load to:
```
entrada_default = quantize_brl(entrada_minima_pct * valor_veiculo.default)
```
This replaces the current hardcoded `Decimal("10000")` default.

### % Indicator label
A `ui.label` placed directly below the `valor_entrada` input:

```
"12.5%  (min. 10%)"
```

**Color logic:**
| Condition | CSS class |
|-----------|-----------|
| current % >= `entrada_minima_pct` | `text-slate-400` |
| current % < `entrada_minima_pct` | `text-amber-500` |
| `valor_veiculo` is zero | label hidden |

**Update trigger:** both `valor_veiculo` and `valor_entrada` gain `on_change` callbacks that call `_update_pct_label()`. Exact binding depends on `CurrencyInput`'s event API (resolved during implementation).

### Behavior after user edits
The user owns the field immediately after touching it. There is no automatic recalculation of `valor_entrada` when `valor_veiculo` changes — the % indicator continues to reflect the current state.

---

## Feature 3: Taxa Mensal — BACEN Pre-fill + Live Update

### Pre-fill
```python
taxa_initial = taxa_bacen_val if taxa_bacen_val is not None else Decimal("0")
taxa = PercentInput("Taxa mensal", taxa_initial)
```

### BACEN hint label
A `ui.label` directly below `taxa`, styled `text-xs italic`:

| State | Text | Color |
|-------|------|-------|
| Data loaded | `"BACEN TX_VEIC: 1.89% a.m."` | `text-slate-400` |
| No data | `"sem dados BACEN — informe manualmente"` | `text-amber-500` |

The hint reflects the DB value, not the current input value.

### Live update (reactive polling)
```python
taxa_modified = {"v": False}

def _on_taxa_change():
    taxa_modified["v"] = True

def _poll_bacen():
    with SessionLocal() as session:
        row = IndicatorRepository(session).get_latest("TX_BACEN_VEIC")
        new_val: Decimal | None = row.valor if row else None
    if new_val is None:
        return
    bacen_hint.set_text(f"BACEN TX_VEIC: {new_val * 100:.2f}% a.m.")
    bacen_hint.classes("text-slate-400", replace=True)
    bacen_hint.update()
    if not taxa_modified["v"]:
        taxa.value = row.valor
        taxa.update()

ui.timer(60, _poll_bacen)
```

**State transitions:**

```
page opens, no data  ->  taxa=0.00%, hint=amber "sem dados BACEN — informe manualmente"
timer fires, data arrives  ->  taxa=1.89% (auto), hint=gray "BACEN TX_VEIC: 1.89% a.m."
user edits taxa manually  ->  taxa=user value, taxa_modified=True; hint still updates on poll
subsequent polls  ->  taxa unchanged (flag set), hint refreshes with latest BACEN value
```

---

## Files Changed

| File | Change |
|------|--------|
| `app/ui/pages/simulacao.py` | Add 3 imports; read page data in `content()`; add cliente selector, entrada default + % label, taxa default + hint + timer |

No other files are modified.

---

## Out of Scope

- Persisting `cliente_id` into the proposal/PDF (future work).
- Displaying client details (phone, email, renda) after selection.
- Filtering the client list by type (PF/PJ).
- Debounced server-side client search (not needed at current scale).
