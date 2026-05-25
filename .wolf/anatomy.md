# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-25T19:45:57.985Z
> Files: 10 tracked | Anatomy hits: 0 | Misses: 0

## ./


## .claude/


## .claude/rules/


## .github/workflows/


## app/

- `main.py` — FinacialSim entry point - boots NiceGUI in a pywebview window. (~1052 tok)

## app/core/


## app/data/


## app/data/migrations/


## app/data/migrations/versions/


## app/integrations/


## app/integrations/bacen/


## app/integrations/fipe/

- `parallelum.py` — FIPE Parallelum primary provider. (~969 tok)

## app/services/

- `scheduler.py` — Scheduler - APScheduler wiring for background jobs (indicators + backup). (~770 tok)

## app/ui/

- `layout.py` — Common layout - sidebar + header. Used by all pages except /login. (~1150 tok)
- `theme.py` — Cores, tipografia, espaçamentos da UI. (~1956 tok)

## app/ui/components/

- `kpi_card.py` — KPI card - label + big value + optional secondary text + hide toggle. (~491 tok)

## app/ui/pages/

- `fipe.py` — FIPE vehicle price lookup page. (~1607 tok)
- `simulacao.py` — Simulacao page - the central tab. (~3298 tok)

## app/utils/


## assets/


## docs/


## docs/agents/


## docs/superpowers/plans/


## docs/superpowers/specs/


## scripts/

- `build_exe.py` — Cross-platform PyInstaller builder. (~366 tok)
- `finacialsim.spec` — -*- mode: python ; coding: utf-8 -*- (~447 tok)

## tests/integration/


## tests/unit/core/


## tests/unit/data/


## tests/unit/integrations/


## tests/unit/integrations/bacen/


## tests/unit/integrations/fipe/


## tests/unit/services/


## tests/unit/utils/

