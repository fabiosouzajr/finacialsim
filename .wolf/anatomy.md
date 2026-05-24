# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-24T15:04:37.254Z
> Files: 41 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.gitignore` — Git ignore rules (~866 tok)
- `alembic.ini` (~177 tok)
- `pyproject.toml` — Simulador de financiamento de veiculos - bank-grade (~240 tok)

## .claude/

- `settings.json` (~503 tok)

## .claude/rules/


## app/core/

- `amortization.py` — Amortizacao extraordinaria (quitacoes parciais/total). (~1119 tok)
- `cet.py` — CET (Custo Efetivo Total) via TIR (pure-Python bisection). (~559 tok)
- `extras.py` — Custos adicionais mensais (extras) acrescidos a parcela. (~614 tok)
- `iof.py` — IOF veiculo (Decreto 6.306/2007) - opcional por simulacao. (~854 tok)
- `money.py` — Decimal helpers and bank-grade rounding for FinacialSim. (~221 tok)
- `price_table.py` — Tabela Price com dias corridos (convencao BACEN/CCB veiculos). (~1200 tok)
- `rate_suggestions.py` — Curva de taxa sugerida por prazo. Loaded from DB in Phase 2; pure function here. (~242 tok)
- `validators.py` — Business rule validations for simulation inputs. (~1022 tok)

## app/data/

- `__init__.py` (~0 tok)
- `backup.py` — backup_sqlite, restore_sqlite, list_backups, prune_backups (~590 tok)
- `database.py` — Base: create_engine_for_sqlite, get_session_factory (~264 tok)
- `models.py` — Declares User (~3880 tok)
- `repositories.py` — UserRepository: create, get, list_active, deactivate + 10 more (~1630 tok)

## app/data/migrations/

- `env.py` — run_migrations_offline, run_migrations_online (~448 tok)

## app/data/migrations/versions/

- `20260524_85a5039acfca_seed_initial_data.py` — seed initial data (~1075 tok)
- `20260524_f7c4f92f22d2_initial_schema.py` — initial schema (~3886 tok)

## docs/agents/


## docs/superpowers/plans/

- `2026-05-23-phase-2-data.md` — Phase 2 — Persistência (SQLAlchemy + Alembic) (~13269 tok)
- `2026-05-23-phase-3-integrations.md` — Phase 3 — Integrações FIPE + BACEN (revised: 10 tasks, retry_error_callback on fetch, FipeCache.acao migration, BACEN TTL read-through) (~15k tok)

## docs/superpowers/specs/


## tests/integration/

- `test_migrations.py` — test_alembic_upgrade_and_seed (~279 tok)
- `test_simulation_flow.py` — End-to-end test exercising the whole core in one simulation. (~614 tok)

## tests/unit/core/

- `test_amortization.py` — test_reduzir_prazo_shortens_schedule, test_reduzir_parcela_keeps_n_lowers_pmt, test_schedule_pmt_is_ (~715 tok)
- `test_cet.py` — test_cet_matches_taxa_when_no_iof_no_tarifas, test_cet_higher_than_taxa_with_iof (~268 tok)
- `test_extras.py` — test_mensal_continuo_all_parcelas, test_rateio_meses_only_first_n, test_multiple_extras_sum_per_parc (~797 tok)
- `test_iof.py` — test_compute_iof_only_fixed_when_n_zero_carencia, test_compute_iof_caps_dias_at_365, test_iof_iterat (~583 tok)
- `test_money.py` — test_centavo_constant, test_quantize_brl_half_up, test_quantize_brl_negatives, test_to_decimal_accep (~241 tok)
- `test_price_table.py` — test_compute_pmt_classic_price_d1_30, test_compute_pmt_one_installment, test_compute_pmt_zero_rate, (~713 tok)
- `test_rate_suggestions.py` — test_suggest_within_first_band, test_suggest_within_third_band, test_suggest_beyond_last_band_uses_l (~244 tok)
- `test_validators.py` — test_valid_input_returns_no_errors, test_entrada_below_minimum_blocks, test_prazo_out_of_range_block (~782 tok)

## tests/unit/data/

- `__init__.py` (~0 tok)
- `conftest.py` — session (~147 tok)
- `test_backup.py` — test_backup_creates_gz_file, test_list_backups_returns_chronological, test_restore_overwrites_target (~537 tok)
- `test_database.py` — test_create_engine_creates_file, test_session_factory_returns_callable (~306 tok)
- `test_models_misc.py` — test_business_rule_unique_chave, test_indicator_history_unique_codigo_data, test_audit_log, test_app (~374 tok)
- `test_models_simulation.py` — test_create_simulation_with_extras_and_fees, test_amortization_row_persists (~1054 tok)
- `test_models_users_clients.py` — test_create_user, test_create_client_with_creator (~200 tok)
- `test_repositories_misc.py` — test_client_create_and_find_by_cpf, test_indicator_upsert, test_business_rule_get, test_simulation_c (~1251 tok)
- `test_repositories_users.py` — test_create_and_get, test_list_active_only (~193 tok)
