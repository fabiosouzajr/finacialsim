# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-23

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

## Key Learnings

- **Project:** finacialsim
- **Windows SQLite test cleanup:** On Windows, temp databases remain locked after session ends. Always call `engine.dispose()` in test fixtures AFTER the session is closed to release the connection pool and allow directory cleanup.
- **CPF/CNPJ validation:** Modulo-11 checks handle both CPF (11 digits) and CNPJ (14 digits). Algorithm: compute weighted sum, mod 11, then map 10→0. All-same-digit (11111111111, etc.) are always invalid.

- **Virtual environment:** Always use `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/Mac) instead  
    of the system `python` when running commands in this project. The system Python lacks project dependencies (nicegui,  
    loguru, etc.). Check for `.venv/` at the repo root before running any `python` or `pytest` command, and prefix all
    such commands with the venv interpreter path.

## Do-Not-Repeat

- [2026-05-25] Running `python` or `pytest` directly fails with `ModuleNotFoundError` because project deps are in
    `.venv`. Always use `.venv/Scripts/python.exe -m pytest` (Windows) or `.venv/bin/python -m pytest` (Linux/Mac).
- [2026-05-25] **NiceGUI smoke tests**: Do NOT use the `user` fixture from `nicegui.testing.user_plugin` — it requires `main.py` at project root. Instead, use `user_simulation()` async context manager directly. Also, `apply_global_styles()` uses `ui.add_head_html()` which requires an active page context — cannot be called outside a `@ui.page` handler in tests.
<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->

## Decision Log

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
- [2026-05-23] **CET root finder**: Replace `scipy.optimize.brentq` + `numpy` with a pure-Python bisection loop. Rationale: only one call site, function is smooth, avoids ~35MB C-extension deps. If curve fitting or matrix ops are needed in Phase 4+, re-evaluate.
- [2026-05-23] **CET timing model**: Use `meses = row.numero_parcela * (d1 / 30.0)` instead of `(row.data_vencimento - data_liberacao).days / 30.0`. Preserves the invariant that CET == taxa when no IOF/extras. `compute_cet` receives `d1: int = 30`; `data_liberacao` param can be removed as it becomes unused.
- [2026-05-23] **All deps at install**: All pyproject.toml deps declared upfront (including weasyprint, nicegui, etc.). Environment is assumed pre-configured on Windows.
- [2026-05-23] **Rate curve**: DB-backed (Phase 2). `suggest_rate` stays pure; service layer fetches from DB and passes the list in. Phase 1 tests use hardcoded fixture.
- [2026-05-23] **`_rebuild_segment` d1**: Hardcoded at 30. Treat post-payment saldo as fresh 30-day loan anchored on next vencimento. Documented assumption, not a parameter.
- [2026-05-23] **`tolerancia`/`max_iteracoes` in IOF iteration**: Removed from public signature. Hardcoded internally (0.01 and 10). Only public knob is `incluir_iof: bool`.
- [2026-05-23] **`taxa_minima_mes` validation**: Demoted to WARNING (not ERROR). Hard ERROR reserved for mathematically broken inputs.
- [2026-05-23] **`RATEIO_MESES` rounding**: Last installment absorbs rounding residual so total matches `valor_total` exactly.
- [2026-05-23] **`Schedule.pmt` after extraordinary amortization**: Carries the correct uniform PMT (not last row's adjusted parcela). REDUZIR_PARCELA uses `new_pmt`; REDUZIR_PRAZO uses `pmt_original`.
