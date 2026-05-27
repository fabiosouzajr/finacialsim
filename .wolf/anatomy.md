# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-27T14:31:13.847Z
> Files: 30 tracked | Anatomy hits: 0 | Misses: 0

## ./


## .claude/


## .claude/rules/


## .github/workflows/


## .superpowers/brainstorm/472-1779808804/content/

- `veiculos-layout.html` (~1999 tok)

## .superpowers/brainstorm/916-1779811579/content/

- `simulacao-veiculo.html` (~2092 tok)
- `veiculos-layout-v2.html` (~1531 tok)
- `veiculos-layout.html` (~1999 tok)

## app/

- `main.py` — FinacialSim entry point - boots NiceGUI in a pywebview window. (~1044 tok)

## app/core/


## app/data/

- `models.py` — Declares User (~4137 tok)

## app/data/migrations/


## app/data/migrations/versions/

- `20260526_45b4fea970eb_add_vehicle_fields.py` — add_vehicle_fields (~699 tok)

## app/integrations/


## app/integrations/bacen/


## app/integrations/fipe/


## app/reports/


## app/services/

- `client_service.py` — ClientService - validated client CRUD. (~825 tok)
- `vehicle_service.py` — VehicleService — full CRUD: placa validation, create_from_fipe, create_manual, set_status, update, refresh_fipe, list_active, list_all, get_simulations. (~2100 tok)

## app/ui/

- `error_handler.py` — handle_unexpected(exc, context): logs via loguru + shows generic toast. Imported by simulacao.py and veiculos.py event handlers. (~120 tok)
- `layout.py` — Common layout - sidebar + header. Used by all pages except /login. (~1127 tok)
- `theme.py` — Cores, tipografia, espaçamentos da UI. (~2231 tok)

## app/ui/components/

- `charts.py` — Plotly chart factories for the simulation UI. (~606 tok)
- `percent_input.py` — PercentInput - input as % (display) -> Decimal fraction (model). (~459 tok)

## app/ui/pages/

- `cadastro.py` — Cadastro page - clientes + usuarios sub-tabs. (~1463 tok)
- `configuracoes.py` — Configuracoes - edit business_rules. (~1754 tok)
- `login.py` — Login page - PIN-based auth. (~514 tok)
- `simulacao.py` — Simulacao page - the central tab. (~8838 tok)
- `veiculos.py` — Vehicle registry page. (~7946 tok)

## app/utils/


## assets/


## docs/


## docs/agents/


## docs/superpowers/plans/

- `2026-05-26-simulacao-smart-defaults.md` — Simulacao Smart Defaults Implementation Plan (~4554 tok)
- `2026-05-26-ui-error-feedback.md` — UI Error Feedback Implementation Plan (~4295 tok)
- `2026-05-26-veiculos.md` — Vehicle Registry Implementation Plan (~19614 tok)
- `2026-05-27-ui-polish.md` — UI Polish Implementation Plan (~3826 tok)

## docs/superpowers/specs/

- `2026-05-26-simulacao-smart-defaults-design.md` — Design Spec — Simulacao Smart Defaults (~1591 tok)
- `2026-05-26-ui-error-feedback-design.md` — Design Spec — UI Error Feedback for Simulation & Vehicle Flows (~1864 tok)
- `2026-05-26-veiculos-design.md` — Design Spec — Cadastro de Veículos (~3643 tok)
- `2026-05-27-ui-polish-design.md` — Design Spec — UI Polish: Login, Cadastro, Simulação, Configurações (~2273 tok)

## scripts/


## tests/integration/

- `test_vehicle_simulation_flow.py` — Integration: vehicle registry → simulation → verify veiculo_id link. (~997 tok)

## tests/unit/core/


## tests/unit/data/

- `test_models_vehicles.py` — test_vehicle_has_new_fields, test_vehicle_status_default (~276 tok)

## tests/unit/integrations/


## tests/unit/integrations/bacen/


## tests/unit/integrations/fipe/


## tests/unit/services/

- `test_vehicle_service.py` — session, svc, quote, test_placa_formato_antigo_normalizado (~2451 tok)

## tests/unit/utils/

