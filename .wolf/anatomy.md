# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-23T18:24:26.734Z
> Files: 21 tracked | Anatomy hits: 0 | Misses: 0

## ./


## .claude/


## .claude/rules/


## .claude/worktrees/phase-1-core/

- `mypy.ini` (~76 tok)
- `pyproject.toml` — Simulador de financiamento de veiculos - bank-grade (~234 tok)
- `pytest.ini` (~40 tok)
- `ruff.toml` — " = ["B", "S"] (~40 tok)

## .claude/worktrees/phase-1-core/app/core/

- `amortization.py` — Amortizacao extraordinaria (quitacoes parciais/total). (~1119 tok)
- `cet.py` — CET (Custo Efetivo Total) via TIR (pure-Python bisection). (~559 tok)
- `extras.py` — Custos adicionais mensais (extras) acrescidos a parcela. (~614 tok)
- `iof.py` — IOF veiculo (Decreto 6.306/2007) - opcional por simulacao. (~854 tok)
- `money.py` — Decimal helpers and bank-grade rounding for FinacialSim. (~221 tok)
- `price_table.py` — Tabela Price com dias corridos (convencao BACEN/CCB veiculos). (~1200 tok)
- `rate_suggestions.py` — Curva de taxa sugerida por prazo. Loaded from DB in Phase 2; pure function here. (~242 tok)
- `validators.py` — Business rule validations for simulation inputs. (~1022 tok)

## .claude/worktrees/phase-1-core/tests/integration/

- `test_simulation_flow.py` — End-to-end test exercising the whole core in one simulation. (~614 tok)

## .claude/worktrees/phase-1-core/tests/unit/core/

- `test_amortization.py` — test_reduzir_prazo_shortens_schedule, test_reduzir_parcela_keeps_n_lowers_pmt, test_schedule_pmt_is_ (~715 tok)
- `test_cet.py` — test_cet_matches_taxa_when_no_iof_no_tarifas, test_cet_higher_than_taxa_with_iof (~268 tok)
- `test_extras.py` — test_mensal_continuo_all_parcelas, test_rateio_meses_only_first_n, test_multiple_extras_sum_per_parc (~797 tok)
- `test_iof.py` — test_compute_iof_only_fixed_when_n_zero_carencia, test_compute_iof_caps_dias_at_365, test_iof_iterat (~583 tok)
- `test_money.py` — test_centavo_constant, test_quantize_brl_half_up, test_quantize_brl_negatives, test_to_decimal_accep (~241 tok)
- `test_price_table.py` — test_compute_pmt_classic_price_d1_30, test_compute_pmt_one_installment, test_compute_pmt_zero_rate,  (~713 tok)
- `test_rate_suggestions.py` — test_suggest_within_first_band, test_suggest_within_third_band, test_suggest_beyond_last_band_uses_l (~244 tok)
- `test_validators.py` — test_valid_input_returns_no_errors, test_entrada_below_minimum_blocks, test_prazo_out_of_range_block (~782 tok)

## docs/agents/


## docs/superpowers/plans/


## docs/superpowers/specs/

