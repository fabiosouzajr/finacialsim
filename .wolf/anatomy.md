# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-28T17:49:04.111Z
> Files: 57 tracked | Anatomy hits: 0 | Misses: 0

## ../../AppData/Local/Temp/

- `architecture-review-20260528.html` — Architecture Review — finacialsim (~9804 tok)

## ./

- `README.md` — Project documentation (~2247 tok)

## .claude/


## .claude/rules/


## .github/workflows/


## .superpowers/brainstorm/472-1779808804/content/

- `veiculos-layout.html` (~1999 tok)

## .superpowers/brainstorm/60-1779893261/content/

- `carne-conteudo.html` (~1570 tok)
- `carne-layout.html` (~1877 tok)
- `carne-pagina.html` (~2091 tok)
- `waiting-1.html` (~39 tok)

## .superpowers/brainstorm/916-1779811579/content/

- `simulacao-veiculo.html` (~2092 tok)
- `veiculos-layout-v2.html` (~1531 tok)
- `veiculos-layout.html` (~1999 tok)

## app/

- `main.py` — FinacialSim entry point - boots NiceGUI in a pywebview window. (~1057 tok)

## app/core/


## app/data/

- `models.py` — Declares User (~4158 tok)

## app/data/migrations/


## app/data/migrations/versions/

- `20260526_45b4fea970eb_add_vehicle_fields.py` — add_vehicle_fields (~699 tok)
- `20260527_a1b2c3d4e5f6_add_carne_fields.py` — add_carne_fields (~490 tok)

## app/integrations/


## app/integrations/bacen/


## app/integrations/fipe/


## app/reports/

- `carne.css` — Styles: 22 rules (~507 tok)
- `carne.html` — Carnê {{ proposal.codigo }} (~511 tok)

## app/services/

- `client_service.py` — ClientService - validated client CRUD. (~825 tok)
- `proposal_service.py` — ProposalService - builds Proposal record + snapshot JSON + PDF rendering. (~3786 tok)
- `simulation_service.py` — SimulationService - orchestrates calculation + persistence. (~3000 tok)
- `vehicle_service.py` — VehicleService — full CRUD: placa validation, create_from_fipe, create_manual, set_status, update, refresh_fipe, list_active, list_all, get_simulations. (~2100 tok)

## app/ui/

- `error_handler.py` — handle_unexpected(exc, context): logs via loguru + shows generic toast. Imported by simulacao.py and veiculos.py event handlers. (~120 tok)
- `layout.py` — Common layout - sidebar + header. Used by all pages except /login. (~1127 tok)
- `theme.py` — Cores, tipografia, espaçamentos da UI. (~2231 tok)

## app/ui/components/

- `charts.py` — Plotly chart factories for the simulation UI. (~606 tok)
- `fipe_picker.py` — FIPE cascade picker — tipo→marca→modelo→ano→price, then saves vehicle. (~1536 tok)
- `percent_input.py` — PercentInput - input as % (display) -> Decimal fraction (model). (~459 tok)

## app/ui/pages/

- `_proposal_helper.py` — Helper to generate PDF from a simulation in UI context. (~398 tok)
- `cadastro.py` — Cadastro page - clientes + usuarios sub-tabs. (~1463 tok)
- `configuracoes.py` — Configuracoes - edit business_rules. (~1870 tok)
- `docs.py` — Documentacao tecnica - renderiza docs/*.md inline. (~396 tok)
- `login.py` — Login page - PIN-based auth. (~514 tok)
- `simulacao.py` — Simulacao page - the central tab. (~8603 tok)
- `veiculos.py` — Vehicle registry page. (~5878 tok)

## app/utils/


## assets/


## docs/


## docs/agents/


## docs/superpowers/plans/

- `2026-05-26-simulacao-smart-defaults.md` — Simulacao Smart Defaults Implementation Plan (~4554 tok)
- `2026-05-26-ui-error-feedback.md` — UI Error Feedback Implementation Plan (~4295 tok)
- `2026-05-26-veiculos.md` — Vehicle Registry Implementation Plan (~19614 tok)
- `2026-05-27-ui-polish.md` — UI Polish Implementation Plan (~3826 tok)
- `2026-05-28-saas-phase-0-foundations.md` — Phase 0 — Foundations Implementation Plan (~10492 tok)

## docs/superpowers/specs/

- `2026-05-23-finacialsim-design.md` — FinacialSim — Design Spec (~13774 tok)
- `2026-05-26-simulacao-smart-defaults-design.md` — Design Spec — Simulacao Smart Defaults (~1591 tok)
- `2026-05-26-ui-error-feedback-design.md` — Design Spec — UI Error Feedback for Simulation & Vehicle Flows (~1864 tok)
- `2026-05-26-veiculos-design.md` — Design Spec — Cadastro de Veículos (~3643 tok)
- `2026-05-27-carne-design.md` — Design Spec — Geração de Carnê PDF (~995 tok)
- `2026-05-27-ui-polish-design.md` — Design Spec — UI Polish: Login, Cadastro, Simulação, Configurações (~2273 tok)
- `2026-05-28-ipva-emplacamento-auto-calc-design.md` — Design Spec — IPVA & Emplacamento Auto-Calculation (~1117 tok)
- `2026-05-28-saas-phase-0-foundations.md` — Phase 0 — Foundations (~1113 tok)
- `2026-05-28-saas-phase-1-auth-rbac.md` — Phase 1 — Auth + RBAC + Tenant management (~1398 tok)
- `2026-05-28-saas-phase-2-simulacao.md` — Phase 2 — Core domain port + Simulação (~1571 tok)
- `2026-05-28-saas-phase-3-cadastros.md` — Phase 3 — Cadastros (Clientes + Veículos + FIPE) (~1091 tok)
- `2026-05-28-saas-phase-4-indicadores-rules.md` — Phase 4 — Indicadores + Business Rules UI + Scheduler + Audit log (~1195 tok)
- `2026-05-28-saas-phase-5-propostas-pdf.md` — Phase 5 — Propostas + PDF/Carnê (worker-rendered) (~1921 tok)
- `2026-05-28-saas-phase-6-portal-cliente-pix.md` — Phase 6 — Portal do cliente + Pix scaffold (~1730 tok)
- `2026-05-28-saas-phase-7-notificacoes.md` — Phase 7 — Notificações (email) + polish (~1423 tok)
- `2026-05-28-saas-roadmap.md` — FinacialSim SaaS — Master Roadmap (~3687 tok)

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

