# FinacialSim

Simulador desktop de financiamento de veículos com precisão bancária real — Tabela Price com dias corridos, IOF, CET via TIR e geração de proposta em PDF.

## Sobre

FinacialSim é um aplicativo desktop para lojas de veículos brasileiras. Permite a vendedores simular financiamentos com a mesma precisão de bancos e financeiras (CCB), cadastrar clientes, consultar a tabela FIPE, comparar cenários e gerar propostas em PDF profissionais. Roda 100% local (SQLite), sem necessidade de servidor.

**Plataformas:** Windows 10+ · Linux (Ubuntu 22.04+) · macOS 12+ (Monterey+)

## Funcionalidades

- Simulação Tabela Price com dias corridos e carência variável
- IOF opcional por simulação (0,38% fixo + 0,0082%/dia, iterado para convergência)
- CET via TIR exata (bisseção pure-Python, convenção BCB)
- Custos adicionais mensais: proteção veicular, IPVA, emplacamento, personalizados
- Consulta FIPE com cascade pickers e cadeia de fallback (Parallelum → BrasilAPI → manual)
- Indicadores econômicos automáticos: SELIC, CDI, IPCA, taxa BACEN veículos
- Proposta em PDF reproduzível com snapshot (WeasyPrint + Jinja2)
- Comparação lado-a-lado de dois cenários
- Amortização extraordinária (reduzir prazo ou reduzir parcela)
- Três perfis de acesso: vendedor / gerente / admin
- Backup automático diário + restauração validada com `PRAGMA integrity_check`
- Cadastro de clientes PF/PJ com validação de CPF/CNPJ (mod-11)

## Pré-requisitos

- Python 3.12+
- **Windows:** GTK+ runtime necessário para o WeasyPrint — [baixar aqui](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
- **Linux:** `sudo apt install libpango-1.0-0 libgdk-pixbuf2.0-0`
- **macOS:** `brew install pango gdk-pixbuf libffi`

## Instalação (desenvolvimento)

```bash
python -m venv .venv
```

```bash
# Windows
.venv\Scripts\python.exe -m pip install -e ".[dev]"

# Linux / macOS
.venv/bin/python -m pip install -e ".[dev]"
```

## Executar

```bash
# Windows
.venv\Scripts\python.exe app/main.py

# Linux / macOS
.venv/bin/python app/main.py
```

O app abre em janela nativa (1400×900). Credenciais padrão no primeiro run: usuário **admin**, PIN **123456** — o sistema solicitará troca no primeiro login.

## Testes

```bash
# Windows — substitua .venv\Scripts\ por .venv/bin/ no Linux/macOS
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m pytest tests/unit/          # apenas unitários
.venv\Scripts\python.exe -m pytest tests/integration/   # apenas integração

# Lint + type check
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy app/
```

## Build do executável

```bash
# Gera dist/FinacialSim/ (Windows)
.venv\Scripts\python.exe scripts/build_exe.py
```

Ver [`docs/INSTALACAO.md`](docs/INSTALACAO.md) para empacotar em Linux (AppImage) e macOS (.app/.dmg).

## Estrutura do projeto

```text
app/
  core/         — matemática financeira pura (Price, IOF, CET, amortização) — zero I/O
  data/         — modelos SQLAlchemy, migrations Alembic, repositórios
  integrations/ — providers FIPE + BACEN com cadeia de fallback
  services/     — orquestração de casos de uso
  ui/           — páginas e componentes NiceGUI
  reports/      — templates HTML/CSS para PDF (WeasyPrint + Jinja2)
  utils/        — formatação BR, validação CPF/CNPJ, logging

tests/unit/        — testes unitários (core financeiro com hypothesis)
tests/integration/ — fluxo completo com SQLite em memória
scripts/           — build PyInstaller, instaladores, seed de demo
docs/              — arquitetura, matemática Price, guia do usuário, troubleshooting
```

## Arquitetura em camadas

```text
UI (NiceGUI / pywebview)
    └── Services  ← único ponto de orquestração
            ├── Core        (matemática pura, sem I/O, testável em isolamento)
            ├── Data        (SQLAlchemy + SQLite + Alembic)
            └── Integrations (FIPE / BACEN com ProviderChain + cache)
```

`core/` não importa de nenhuma outra camada. `ui/` nunca acessa repositórios diretamente — sempre via `services/`.

### Módulos do core (`app/core/`)

| Módulo | Responsabilidade |
| -------- | ----------------- |
| `money.py` | Contexto `Decimal` (28 dígitos, `ROUND_HALF_UP`), constantes de quantização |
| `price_table.py` | Cálculo da parcela PMT e cronograma completo (capitalização exponencial fracionada com `d1` dias corridos) |
| `iof.py` | IOF veículo: 0,38% fixo + 0,0082%/dia por parcela; iteração de convergência quando incorporado ao principal |
| `cet.py` | CET via bisseção pure-Python (200 iter, tol 1e-10) — convenção BCB; extras não entram no CET |
| `amortization.py` | Amortização extraordinária parcial/total nos modos `reduzir_prazo` e `reduzir_parcela` |
| `extras.py` | Custos adicionais mensais: `mensal_continuo`, `rateio_meses`, `unico_inicial` |
| `rate_suggestions.py` | Curva taxa-por-prazo configurável (sugestão, não bloqueio) |
| `validators.py` | Validações de entrada; retorna `ValidationIssue(level, field, message)` |

### Serviços (`app/services/`)

| Serviço | Responsabilidade |
| --------- | ----------------- |
| `simulation_service.py` | Orquestra `core/` + repositórios; persiste simulação e cronograma |
| `proposal_service.py` | Gera PDF via WeasyPrint; snapshot `proposals.snapshot_json` para reprodutibilidade |
| `amortization_service.py` | Aplica pagamentos extras sobre simulação existente |
| `comparison_service.py` | Persiste comparativos A/B em `comparisons` |
| `client_service.py` | CRUD de clientes com validação CPF/CNPJ |
| `vehicle_service.py` | CRUD de veículos: busca FIPE, manual, set_status, refresh_fipe |
| `auth_service.py` | Autenticação PIN/bcrypt, controle de lockout (5 tentativas / 5 min) |
| `indicators_service.py` | Upsert em `indicators_history`; expõe último valor + flag `stale` |
| `rules_service.py` | CRUD de `business_rules` com auditoria |
| `audit_service.py` | Append em `audit_log` com `diff_json` |
| `backup_service.py` | Facade sobre `data/backup.py` para UI e scheduler |
| `scheduler.py` | APScheduler: atualiza indicadores 09h, prune FIPE cache 03h, backup 23h, health-check 6h |

### Páginas (`app/ui/pages/`)

| Página | Rota | Perfis |
| -------- | ------ | -------- |
| `login.py` | `/login` | todos |
| `dashboard.py` | `/dashboard` | todos |
| `cadastro.py` | `/cadastro` | todos (usuários só admin) |
| `simulacao.py` | `/simulacao` | todos |
| `comparativo.py` | `/comparativo` | todos |
| `amortizacao.py` | `/amortizacao` | todos |
| `indicadores.py` | `/indicadores` | todos (editar: gerente/admin) |
| `veiculos.py` | `/veiculos` | todos |
| `configuracoes.py` | `/configuracoes` | admin (gerente: leitura) |
| `logs.py` | `/logs` | gerente/admin |
| `docs.py` | `/docs` | todos |

### APIs externas (`app/integrations/`)

#### FIPE — preço de veículos

| Provider | Base URL | Fallback |
| ---------- | ---------- | ---------- |
| **Parallelum** (primário) | `https://parallelum.com.br/fipe/api/v2` | → BrasilAPI |
| **BrasilAPI** (fallback 1) | `https://brasilapi.com.br/api/fipe` | → manual |
| **Manual** (fallback 2) | — | entrada direta pelo vendedor |

Endpoints Parallelum: `GET /{tipo}/brands`, `.../models`, `.../years`, `.../years/{yearId}`.
Cache em SQLite (`fipe_cache`): 30 dias para listas, 24h para preço unitário.

#### BACEN — indicadores econômicos

| Provider | Base URL | Fallback |
| ---------- | ---------- | ---------- |
| **BCB SGS** (primário) | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados` | → BrasilAPI |
| **BrasilAPI** (fallback 1) | `https://brasilapi.com.br/api/taxas/v1/{indicador}` | → cache local |
| **Cache local** (fallback 2) | `indicators_history` (último valor, marcado `stale`) | — |

Séries consultadas: SELIC meta (432), SELIC diária (11), CDI (12), IPCA (433), taxa BACEN veículos (20714).
Todos os valores normalizados para fração decimal (`Decimal`). Conversões mensal ↔ anual ↔ diária em `bacen/conversions.py`.

## Documentação

| Documento | Conteúdo |
| ----------- | ---------- |
| [`docs/guia_usuario.md`](docs/guia_usuario.md) | Fluxos para vendedores (login, simular, gerar PDF) |
| [`docs/matematica_price.md`](docs/matematica_price.md) | Tabela Price, IOF e CET com derivações completas |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Problemas comuns: GTK runtime, antivírus, banco corrompido |
| [`docs/INSTALACAO.md`](docs/INSTALACAO.md) | Instalação passo a passo em Windows, Linux e macOS |
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Referência técnica viva (modelos, contratos, exemplos) |

## Stack

| Camada | Tecnologia |
| -------- | ------------ |
| UI | NiceGUI 2.x + pywebview 5.x |
| Gráficos | Plotly |
| ORM + migrations | SQLAlchemy 2.x + Alembic |
| Banco | SQLite (WAL) |
| Aritmética financeira | `decimal.Decimal` (28 dígitos, ROUND_HALF_UP) |
| HTTP | httpx + tenacity |
| Validação | Pydantic v2 |
| PDF | WeasyPrint + Jinja2 |
| Auth | bcrypt (PIN 4–6 dígitos) |
| Agendador | APScheduler |
| Logs | loguru |
| Empacotamento | PyInstaller (`--onedir`) |
| Testes | pytest + hypothesis |
