# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-25T13:22:42.070Z
> Files: 28 tracked | Anatomy hits: 0 | Misses: 0

## ./


## .claude/


## .claude/rules/


## app/core/


## app/data/

- `models.py` — Declares User (~3980 tok)

## app/data/migrations/


## app/data/migrations/versions/


## app/integrations/


## app/integrations/bacen/


## app/integrations/fipe/


## app/services/

- `__init__.py` (~0 tok)
- `amortization_service.py` — AmortizationService - applies extraordinary payments to a saved simulation. (~841 tok)
- `audit_service.py` — AuditService - business-event log persisted to audit_log table. (~296 tok)
- `auth_service.py` — AuthService - PIN-based authentication with bcrypt and lockout. (~907 tok)
- `backup_service.py` — BackupService - thin facade over app.data.backup for UI/scheduler. (~220 tok)
- `client_service.py` — ClientService - validated client CRUD. (~736 tok)
- `comparison_service.py` — ComparisonService - compute and persist comparisons between simulations. (~452 tok)
- `indicators_service.py` — IndicatorsService - fetch + cache BACEN indicators. (~471 tok)
- `proposal_service.py` — ProposalService - builds Proposal record + snapshot JSON. PDF in Phase 6. (~1517 tok)
- `rules_service.py` — RulesService - typed access to business_rules. (~500 tok)
- `simulation_service.py` — SimulationService - orchestrates calculation + persistence. (~2482 tok)

## app/utils/

- `__init__.py` (~0 tok)
- `document_validation.py` — CPF and CNPJ validation (modulo-11 checks). (~303 tok)

## docs/agents/


## docs/superpowers/plans/

- `2026-05-23-phase-4-services.md` — Phase 4 — Serviços (orquestração) (~17254 tok)

## docs/superpowers/specs/


## tests/integration/


## tests/unit/core/


## tests/unit/data/


## tests/unit/integrations/


## tests/unit/integrations/bacen/


## tests/unit/integrations/fipe/


## tests/unit/services/

- `__init__.py` (~0 tok)
- `test_amortization_service.py` — session, test_apply_partial_quitacao_reduces_pmt (~533 tok)
- `test_audit_service.py` — session, test_log_creates_audit_entry, test_log_without_diff_stores_none (~399 tok)
- `test_auth_service.py` — session, test_create_user_and_login, test_login_wrong_pin_raises, test_change_pin_works_with_old_pin (~486 tok)
- `test_backup_service.py` — test_backup_now_creates_file (~180 tok)
- `test_client_service.py` — session, test_create_client_with_valid_cpf, test_create_client_invalid_cpf_raises (~334 tok)
- `test_comparison_service.py` — session, test_compare_two_simulations (~598 tok)
- `test_indicators_service.py` — FakeChain: fetch, session_factory, test_update_indicator_persists (~456 tok)
- `test_proposal_service.py` — session, test_create_proposal_persists_snapshot, test_create_clientless_proposal (~829 tok)
- `test_rules_service.py` — session, test_decimal_default_value_when_missing, test_bool_value, test_decimal_value (~383 tok)
- `test_simulation_service.py` — session, test_run_simulation_persists_and_returns, test_run_simulation_with_extras_persists_extras_t (~1176 tok)

## tests/unit/utils/

- `__init__.py` (~0 tok)
- `test_document_validation.py` — test_known_valid_cpf, test_known_invalid_cpf, test_known_valid_cnpj, test_known_invalid_cnpj (~129 tok)
