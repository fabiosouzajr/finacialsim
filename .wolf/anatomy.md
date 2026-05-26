# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-26T15:00:00.000Z
> Files: tracked after full codebase survey

## ./

- `CLAUDE.md` — behavioral guidelines, quickstart, stack, gotchas, OpenWolf ref (~1920 tok)
- `pyproject.toml` — deps: nicegui, sqlalchemy, alembic, pydantic, httpx, bcrypt, weasyprint, loguru, apscheduler, pywebview, plotly; no scipy/numpy (~100 tok)
- `alembic.ini` — alembic config pointing to app/data/migrations/ (~30 tok)

## .claude/

## .claude/rules/

## .github/workflows/

## app/

- `__init__.py` — empty package marker
- `main.py` — entry: `_platform_data_dir`, `_run_migrations` (alembic Python API), build_app, main(); registers all pages (~120 tok)

## app/core/

- `money.py` — Decimal context (prec=28), quantize_brl (ROUND_HALF_UP, 2dp), CENTAVO/PCT_DEC/TAXA_DEC (~50 tok)
- `price_table.py` — build_schedule(PV, i_m, n, d1): Schedule + ScheduleRow; exponential daily rate; last-row residual (~150 tok)
- `iof.py` — calc_iof: iterative convergence; IofResult; tolerância/max_iter hardcoded internally (~120 tok)
- `cet.py` — compute_cet(valor_liberado, schedule, d1=30): pure-Python bisection 200 iter; timing=numero_parcela*(d1/30); CetResult (~80 tok)
- `amortization.py` — apply_extraordinary: REDUZIR_PARCELA/REDUZIR_PRAZO; `_rebuild_segment` d1=30 (~200 tok)
- `extras.py` — apply_extras_to_schedule: mensal_continuo/rateio_meses/unico_inicial; enriches rows with extras_total + parcela_total (~120 tok)
- `rate_suggestions.py` — suggest_rate(prazo, curva): returns suggested monthly rate from curve list (~40 tok)
- `validators.py` — validate_simulation_inputs: ValidationIssue list; taxa_minima is WARNING (~100 tok)

## app/data/

- `database.py` — create_engine_for_sqlite(path), get_session_factory(engine), Base declarative (~50 tok)
- `models.py` — ORM: User, Client, Vehicle, SimulationFee, SimulationExtra, AmortizationRow, ExtraordinaryAmortization, Simulation, Proposal, Comparison, IndicatorHistory, BusinessRule, AuditLog, AppSetting, FipeCache (has `acao` col) (~400 tok)
- `repositories.py` — typed CRUD per entity (~300 tok)
- `backup.py` — backup_sqlite, list_backups, prune_backups, restore_sqlite primitives (~100 tok)

## app/data/migrations/

- `env.py` — alembic env; imports Base.metadata (~60 tok)

## app/data/migrations/versions/

- `20260524_f7c4f92f22d2_initial_schema.py` — creates all tables; seeds admin user + business_rules defaults (~300 tok)
- `20260524_85a5039acfca_seed_initial_data.py` — additional seed data (~80 tok)
- `20260524_20d4cc8a430e_add_fipe_cache_acao_column.py` — adds `acao` TEXT to fipe_cache; updates unique constraint (~60 tok)

## app/integrations/

- `base.py` — Ok[T], Err, Result, Provider Protocol, ProviderChain (~80 tok)
- `http.py` — get_json(url, client): shared httpx helper, timeout 8s, User-Agent FinacialSim/0.1 (~50 tok)
- `factory.py` — build_fipe_chain / build_bacen_chain with cache wrappers (~80 tok)

## app/integrations/bacen/

- `schema.py` — IndicatorPoint dataclass (~40 tok)
- `sgs.py` — BcbSgsProvider: SELIC_META(432)/CDI(12)/IPCA(433)/TX_BACEN_VEIC(20714) (~120 tok)
- `brasilapi.py` — BrasilApiBacenProvider: fallback (~80 tok)
- `cached.py` — CachedBacenProvider: TTL decorator over indicators_history (~80 tok)
- `conversions.py` — rate unit conversions: mensal↔anual↔diária(252) (~60 tok)

## app/integrations/fipe/

- `schema.py` — VehicleQuote dataclass (~60 tok)
- `parallelum.py` — ParallelumFipeProvider (~120 tok)
- `brasilapi.py` — BrasilApiFipeProvider: fallback (~80 tok)
- `cache.py` — CachedFipeProvider: listas TTL 720h, preço TTL 24h; uses fipe_cache.acao column (~100 tok)
- `manual.py` — ManualFipeProvider: fonte='manual' (~40 tok)

## app/services/

- `simulation_service.py` — SimulationService.create: orchestrates price_table+iof+cet+extras+rows; persists (~250 tok)
- `amortization_service.py` — AmortizationService.apply_extraordinary: wraps core; persists new schedule (~150 tok)
- `comparison_service.py` — ComparisonService.create: persists Comparison; returns diff dict (~100 tok)
- `proposal_service.py` — ProposalService.generate: snapshot_json; Jinja2+WeasyPrint PDF (~200 tok)
- `client_service.py` — ClientService: create/update/search; CPF/CNPJ via utils/document_validation.py (~120 tok)
- `auth_service.py` — AuthService: verify_pin (bcrypt), lockout, audit_log("login") (~80 tok)
- `indicators_service.py` — IndicatorsService.update_indicator: calls bacen_chain, upserts indicators_history (~100 tok)
- `audit_service.py` — AuditService.log: writes AuditLog row (~50 tok)
- `backup_service.py` — BackupService: thin facade over data/backup.py (~60 tok)
- `rules_service.py` — RulesService: get/set business_rules; audit-logs each change (~80 tok)
- `scheduler.py` — APScheduler: indicators daily 09:00, backup daily 23:00, prune_fipe_cache daily 03:00 (~120 tok)

## app/ui/

- `theme.py` — apply_global_styles(): global CSS via ui.add_head_html(shared=True) (~60 tok)
- `layout.py` — TABS list (label, route, allowed_roles, icon); shell(): header + sidebar with role guards (~100 tok)
- `router.py` — navigate, get_logged_perfil, logout, guard helpers (~60 tok)

## app/ui/components/

- `currency_input.py` — CurrencyInput: BRL-formatted number input (~60 tok)
- `percent_input.py` — PercentInput: %-formatted number input (~50 tok)
- `kpi_card.py` — KpiCard(label, value, icon, color) (~50 tok)
- `amortization_table.py` — AmortizationTable(rows): expandable schedule grid with extras columns (~100 tok)
- `charts.py` — Plotly helpers: balance chart, composition chart, parcela curve (~120 tok)

## app/ui/pages/

- `login.py` — /login: user dropdown + PIN; auth_service; lockout display (~120 tok)
- `dashboard.py` — /dashboard: KPI cards, recent simulations, indicator mini-cards (~150 tok)
- `cadastro.py` — /cadastro: clients table + modal (PF/PJ toggle); admin user sub-tab (~200 tok)
- `simulacao.py` — /simulacao: 3-column layout; debounced recalc; extras panel; IOF toggle (~350 tok)
- `comparativo.py` — /comparativo: A/B side-by-side diff table + overlapping charts (~200 tok)
- `amortizacao.py` — /amortizacao: overlay original vs new schedule; extraordinary payment panel (~200 tok)
- `indicadores.py` — /indicadores: indicator cards; 12-month history; conversion table (~150 tok)
- `fipe.py` — /fipe: cascading dropdowns Tipo→Marca→Modelo→Ano; VehicleQuote result (NEW - not in original spec) (~150 tok)
- `configuracoes.py` — /configuracoes: general settings, business rules editor, IOF rates, backup, appearance (~250 tok)
- `apis.py` — /apis: provider health + manual refresh (FILE EXISTS but NOT registered in main.py — pending) (~150 tok)
- `logs.py` — /logs: paginated audit_log with filters and diff_json detail (~120 tok)
- `docs.py` — /docs: embedded markdown viewer for guia_usuario/matematica/troubleshooting (~80 tok)
- `_proposal_helper.py` — internal helpers: open PDF, show status (~60 tok)

## app/reports/

- `proposta.html` — Jinja2 template → WeasyPrint PDF; all sections from spec §9.1 (~200 tok)
- `proposta.css` — PDF stylesheet: A4, Inter font, color palette, page-break rules (~80 tok)

## app/utils/

- `br_format.py` — format_brl, format_pct, format_date (~40 tok)
- `document_validation.py` — is_valid_cpf, is_valid_cnpj: modulo-11 (~60 tok)
- `logger.py` — setup_logging(log_dir): loguru; daily rotation, 30d retention, gzip after 7d (~50 tok)

## assets/

- icon files for PyInstaller packaging

## docs/

## docs/agents/

## docs/superpowers/plans/

## docs/superpowers/specs/

- `2026-05-23-finacialsim-design.md` — FinacialSim design spec, updated 2026-05-26 to reflect implemented state (~13500 tok)

## scripts/

## tests/integration/

- `test_migrations.py`, `test_full_flow.py`, `test_simulation_flow.py`

## tests/unit/core/

- `test_money.py`, `test_price_table.py`, `test_iof.py`, `test_cet.py`, `test_amortization.py`, `test_extras.py`, `test_rate_suggestions.py`, `test_validators.py`

## tests/unit/data/

- `conftest.py`, `test_database.py`, `test_backup.py`, `test_models_users_clients.py`, `test_models_simulation.py`, `test_models_misc.py`, `test_repositories_users.py`, `test_repositories_misc.py`

## tests/unit/integrations/

- `conftest.py`, `test_base.py`, `test_factory.py`, `test_ui_smoke.py`

## tests/unit/integrations/bacen/

- `test_sgs.py`, `test_brasilapi.py`, `test_cached.py`, `test_conversions.py`

## tests/unit/integrations/fipe/

- `test_parallelum.py`, `test_brasilapi.py`, `test_cache.py`, `test_manual.py`

## tests/unit/services/

- `test_simulation_service.py`, `test_amortization_service.py`, `test_comparison_service.py`, `test_proposal_service.py`, `test_proposal_render.py`, `test_client_service.py`, `test_auth_service.py`, `test_indicators_service.py`, `test_audit_service.py`, `test_backup_service.py`, `test_rules_service.py`, `test_scheduler.py`

## tests/unit/utils/

- `test_br_format.py`, `test_document_validation.py`
