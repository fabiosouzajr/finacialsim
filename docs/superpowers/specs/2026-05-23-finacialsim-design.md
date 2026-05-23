# FinacialSim — Design Spec

> Sistema interno de simulação de financiamento de veículos para uso em loja de carros no Brasil.
> Cálculo financeiro nível banco real (Tabela Price com dias corridos, IOF, CET via TIR).
>
> **Data:** 2026-05-23
> **Status:** Spec aprovado, pronto para `writing-plans`
> **Idioma do produto:** PT-BR (R$, dd/mm/yyyy, separador decimal vírgula)
> **Plataformas:** Windows 10+ e Linux (Ubuntu/Debian/Fedora) — instalação local

---

## 1. Objetivos e capacidades

FinacialSim é um aplicativo desktop multi-perfil para uma loja brasileira, com cálculo financeiro fiel ao praticado por bancos e financeiras brasileiras para CCB de veículos. Os objetivos primários são:

1. Permitir a vendedores leigos simular financiamentos com precisão bancária, em poucos cliques.
2. Vincular simulações a clientes cadastrados e gerar propostas em PDF profissionais.
3. Manter taxas e indicadores econômicos sempre atualizados, com fallback robusto a falhas de rede.
4. Comparar cenários e simular amortizações extraordinárias (parcial, total, reduzir prazo, reduzir parcela).
5. Manter histórico auditável e reproduzível (uma proposta de 2026 deve poder ser regerada em 2027, idêntica).
6. Servir de base modular para futuras integrações (CRM, WhatsApp, geração de carnê, APIs bancárias).

Capacidades resumidas:

- Cadastro de clientes (PF/PJ) com validação de CPF/CNPJ.
- Consulta FIPE com filtros encadeados (tipo → marca → modelo → ano).
- Atualização automática de SELIC, CDI, IPCA, taxa BACEN de veículos, IOF.
- Simulação Tabela Price com dias corridos e primeiro vencimento variável.
- IOF (0,38% fixo + 0,0082%/dia, teto 365 dias) iterado para convergência quando incorporado ao principal.
- CET via TIR exata (Brent).
- Cronograma de amortização completo, com gráficos interativos.
- Comparação lado-a-lado de dois cenários.
- Amortização extraordinária com escolha de modo (parcela ou prazo).
- Geração de PDF de proposta com snapshot reproduzível.
- Backup automático e restauração do banco.
- Logs de execução (técnico) e audit log (negócio).
- Três perfis: vendedor / gerente / administrador.

---

## 2. Decisões arquiteturais aprovadas

| Decisão | Escolha | Justificativa |
|---|---|---|
| Modelo de uso | 1 PC compartilhado pela equipe, SQLite local | Atende a maioria das lojas pequenas/médias |
| Stack de UI | **NiceGUI** (Quasar/Vue) em janela nativa via pywebview | Visual profissional, multiplataforma, alto reuso de componentes |
| Precisão financeira | IOF + tarifas + CET via TIR, modo "banco real" | Requisito explícito do cliente |
| Autenticação | PIN numérico 4–6 dígitos por usuário (bcrypt) | Rápido para vendedor, ainda rastreável |
| Arquitetura interna | Monolito modular em camadas (`core` / `data` / `integrations` / `services` / `ui`) | Permite trocar UI ou expor API REST no futuro sem reescrever o core |
| Banco | SQLite + WAL + Alembic migrations | Simples, embutido, evoluível |
| Aritmética | `decimal.Decimal` com `ROUND_HALF_UP`, contexto 28 dígitos | Sem `float` em qualquer ponto financeiro |
| PDF | WeasyPrint (HTML/CSS → PDF) | Templates ricos, reaproveita CSS da UI |
| Empacotamento | PyInstaller `--onedir` + NSIS (Win) / AppImage (Linux) | Instalação fácil sem Python no host |

---

## 3. Stack tecnológica

| Função | Biblioteca | Notas |
|---|---|---|
| UI | NiceGUI + pywebview | Janela nativa ou navegador |
| Gráficos | Plotly + ECharts (embutidos via NiceGUI) | Interativos, exportáveis |
| ORM + migrations | SQLAlchemy 2.x + Alembic | `NUMERIC(18,4)` para campos financeiros |
| Banco | SQLite (WAL) | Embutido |
| Cálculo financeiro | `decimal.Decimal` + `scipy.optimize.brentq` (TIR) | `numpy_financial` para utilitários |
| HTTP | httpx (async) + tenacity (retry) | Timeout 8s, retry exponencial 3× |
| Validação | Pydantic v2 | Schemas para forms, configs, providers |
| PDF | WeasyPrint + Jinja2 | Template HTML/CSS |
| Localização | Babel + helpers próprios | R$, %, dd/mm/yyyy |
| Auth | bcrypt | PIN hashado |
| Logs | loguru | Rotação diária, gzip após 7 dias |
| Empacotamento | PyInstaller | `--onedir`; NSIS (Win), AppImage (Linux) |
| Agendador | APScheduler | Updates de indicadores, backup, health-check |
| Testes | pytest + hypothesis | Property tests para o core financeiro |

---

## 4. Estrutura de diretórios

```
finacialsim/
├── app/
│   ├── __init__.py
│   ├── main.py                    # ponto de entrada; inicia NiceGUI + pywebview
│   ├── config/
│   │   ├── settings.py            # Pydantic Settings (env + TOML)
│   │   └── rules.py               # regras de negócio configuráveis
│   │
│   ├── core/                      # DOMÍNIO PURO — sem dependência de UI/DB
│   │   ├── money.py               # Decimal + arredondamento bancário
│   │   ├── price_table.py         # Tabela Price exata + dias corridos
│   │   ├── iof.py                 # IOF veículo (0,38% + 0,0082%/dia)
│   │   ├── cet.py                 # CET via TIR (Brent)
│   │   ├── amortization.py        # cronograma + amortização extraordinária
│   │   ├── rate_suggestions.py    # taxa sugerida por prazo
│   │   └── validators.py          # entrada mínima, prazos válidos
│   │
│   ├── data/                      # PERSISTÊNCIA
│   │   ├── models.py              # ORM SQLAlchemy
│   │   ├── repositories.py        # CRUD tipado por entidade
│   │   ├── migrations/            # Alembic
│   │   └── backup.py              # backup automático SQLite
│   │
│   ├── integrations/              # APIs EXTERNAS — chain de fallback
│   │   ├── base.py                # Protocol Provider + ProviderChain
│   │   ├── fipe/
│   │   │   ├── parallelum.py      # primário
│   │   │   ├── brasilapi.py       # fallback
│   │   │   └── manual.py          # entrada manual
│   │   └── bacen/
│   │       ├── sgs.py             # SELIC/CDI/IPCA via api.bcb.gov.br
│   │       ├── brasilapi.py       # fallback
│   │       └── cached.py          # cache em disco
│   │
│   ├── services/                  # ORQUESTRAÇÃO (caso-de-uso)
│   │   ├── simulation_service.py
│   │   ├── comparison_service.py
│   │   ├── amortization_service.py
│   │   ├── proposal_service.py    # gera PDF
│   │   ├── client_service.py
│   │   ├── auth_service.py
│   │   ├── indicators_service.py
│   │   └── audit_service.py
│   │
│   ├── ui/                        # NiceGUI — só apresentação
│   │   ├── theme.py
│   │   ├── components/
│   │   │   ├── currency_input.py
│   │   │   ├── percent_input.py
│   │   │   ├── kpi_card.py
│   │   │   ├── amortization_table.py
│   │   │   └── charts.py
│   │   ├── pages/
│   │   │   ├── login.py
│   │   │   ├── cadastro.py
│   │   │   ├── dashboard.py
│   │   │   ├── simulacao.py
│   │   │   ├── comparativo.py
│   │   │   ├── amortizacao.py
│   │   │   ├── indicadores.py
│   │   │   ├── configuracoes.py
│   │   │   ├── apis.py
│   │   │   ├── logs.py
│   │   │   └── docs.py
│   │   └── router.py              # navegação + guards por perfil
│   │
│   ├── reports/
│   │   └── proposta.html          # template Jinja2 → WeasyPrint
│   │
│   └── utils/
│       ├── br_format.py
│       ├── logger.py
│       └── scheduler.py
│
├── tests/
│   ├── unit/core/                 # bateria pesada de cálculo
│   ├── unit/services/
│   └── integration/
│
├── scripts/
│   ├── install_windows.ps1
│   ├── install_linux.sh
│   ├── build_exe.py
│   └── seed_demo.py
│
├── docs/
│   ├── ARQUITETURA.md
│   ├── DOCUMENTACAO.md
│   ├── guia_usuario.md
│   ├── matematica_price.md
│   └── troubleshooting.md
│
├── data/                          # banco + backups (gerado em runtime)
├── logs/
├── pyproject.toml
├── alembic.ini
└── README.md
```

### Princípios de camadas

- `core/` **não importa** de `ui/`, `data/`, `integrations/` ou `services/`. É puro, testável e reaproveitável.
- `services/` é a única camada que orquestra `core/` + `data/` + `integrations/`.
- `ui/` jamais toca repositórios ou providers diretamente — sempre via `services/`.
- `integrations/` segue `ProviderChain` (primário → secundário → manual), isolando fragilidade.

---

## 5. Modelo de dados (SQLite + SQLAlchemy)

Todas as colunas financeiras são `NUMERIC(18,4)` (Decimal no ORM). Datas usam tipos SQLAlchemy `Date`/`DateTime` (ISO-8601 no SQLite).

### 5.1 Usuários e clientes

**`users`**
- `id` PK
- `nome` TEXT NOT NULL
- `pin_hash` TEXT NOT NULL (bcrypt)
- `perfil` TEXT NOT NULL — `vendedor` | `gerente` | `admin`
- `ativo` BOOLEAN DEFAULT 1
- `criado_em`, `atualizado_em`, `ultimo_login` DATETIME

**`clients`**
- `id` PK
- `nome` TEXT NOT NULL
- `cpf_cnpj` TEXT UNIQUE — validado mod-11
- `tipo` TEXT — `PF` | `PJ`
- `rg`, `data_nasc`, `profissao`, `renda` (NUMERIC 18,2)
- `telefone`, `email`
- `endereco_json` TEXT — logradouro, número, complemento, bairro, cidade, UF, CEP
- `observacoes` TEXT
- `criado_por` FK→`users.id`
- `criado_em`, `atualizado_em`

### 5.2 Veículos e simulações

**`vehicles`** (snapshot por simulação)
- `id` PK
- `fonte` TEXT — `fipe_parallelum` | `fipe_brasilapi` | `manual`
- `tipo`, `marca`, `modelo`, `ano_modelo` INTEGER, `combustivel`
- `codigo_fipe` TEXT
- `valor_fipe` NUMERIC(18,2)
- `valor_referencia` NUMERIC(18,2) — valor real usado
- `mes_referencia_fipe` TEXT
- `snapshot_json` TEXT — payload bruto da API (auditável)
- `criado_em`

**`simulations`**
- `id` PK
- `codigo` TEXT UNIQUE — `SIM-2026-00123`
- `cliente_id` FK→`clients.id` NULLABLE
- `veiculo_id` FK→`vehicles.id`
- `criado_por` FK→`users.id`
- `valor_veiculo`, `valor_entrada` NUMERIC(18,2)
- `pct_entrada` NUMERIC(7,4)
- `prazo_meses` INTEGER
- `taxa_juros_mes` NUMERIC(10,8) — fração (0.01650000 = 1,65% a.m.)
- `taxa_juros_ano` NUMERIC(10,8) — equivalente anual
- `data_liberacao`, `data_primeiro_venc` DATE
- `dias_carencia` INTEGER — derivado
- `iof_total`, `tarifas_total`, `valor_financiado`, `valor_parcela`, `total_pago`, `total_juros` NUMERIC(18,2)
- `pct_juros` NUMERIC(7,4)
- `cet_mes`, `cet_ano` NUMERIC(10,8)
- `status` TEXT — `rascunho` | `finalizada` | `arquivada`
- `rules_snapshot_json` TEXT — regras vigentes na criação (reproduzibilidade)
- `criado_em`, `atualizado_em`

**`simulation_fees`**
- `id` PK
- `simulation_id` FK→`simulations.id`
- `nome` TEXT — `Cadastro`, `Avaliação`, `Registro`, custom
- `valor` NUMERIC(18,2)
- `incluir_no_principal` BOOLEAN

**`amortization_rows`**
- `id` PK
- `simulation_id` FK→`simulations.id` (índice)
- `numero_parcela` INTEGER
- `data_vencimento` DATE
- `dias_periodo` INTEGER
- `saldo_anterior`, `juros`, `amortizacao`, `parcela`, `saldo_devedor` NUMERIC(18,4)
- `ajuste_arredondamento` NUMERIC(18,4) — resíduo na última parcela

**`extraordinary_amortizations`**
- `id` PK
- `simulation_id` FK→`simulations.id`
- `data` DATE
- `valor` NUMERIC(18,2)
- `modo` TEXT — `reduzir_parcela` | `reduzir_prazo`
- `tipo` TEXT — `parcial` | `total`
- `aplicado_em` DATETIME

### 5.3 Propostas e comparações

**`proposals`**
- `id` PK
- `codigo` TEXT UNIQUE — `PROP-2026-00123`
- `simulation_id` FK→`simulations.id`
- `cliente_id` FK→`clients.id`
- `gerado_por` FK→`users.id`
- `snapshot_json` TEXT — tudo congelado para reproduzir o PDF
- `pdf_path` TEXT
- `validade_dias` INTEGER
- `gerado_em` DATETIME

**`comparisons`**
- `id` PK
- `simulation_a_id`, `simulation_b_id` FK→`simulations.id`
- `criado_por` FK→`users.id`
- `criado_em`

### 5.4 Indicadores, regras, auditoria, config

**`indicators_history`**
- `id` PK
- `codigo` TEXT — `SELIC` | `CDI` | `IPCA` | `IOF_FIXO` | `IOF_DIARIO` | `TX_BACEN_VEIC`
- `data_referencia` DATE
- `valor` NUMERIC(12,8) — sempre em fração decimal
- `unidade` TEXT — `pct_aa` | `pct_am` | `pct_ad`
- `fonte` TEXT — `bcb_sgs` | `brasilapi` | `manual`
- `payload_json` TEXT
- `coletado_em` DATETIME
- UNIQUE(`codigo`, `data_referencia`)

**`business_rules`**
- `id` PK
- `chave` TEXT UNIQUE — `entrada_minima_pct`, `taxa_por_prazo_curva`, `iof_fixo_pct`, `iof_diario_pct`, `dias_max_carencia`, `prazo_minimo_meses`, `prazo_maximo_meses`, `taxa_minima_mes`, `taxa_maxima_mes`, `valor_minimo_financiado`
- `valor_json` TEXT
- `descricao` TEXT
- `atualizado_em`, `atualizado_por` FK→`users.id`

**`audit_log`**
- `id` PK
- `timestamp` DATETIME
- `usuario_id` FK→`users.id`
- `acao` TEXT — `login`, `sim_criada`, `sim_editada`, `proposta_gerada`, `config_alterada`, `migration_applied`, etc.
- `entidade`, `entidade_id`
- `diff_json` TEXT — antes/depois
- `ip`, `hostname` TEXT

**`app_settings`**
- `chave` PK TEXT
- `valor_json` TEXT
- `atualizado_em` DATETIME

**`fipe_cache`**
- `id` PK
- `tipo`, `marca_id`, `modelo_id`, `ano_id` TEXT
- `payload_json` TEXT
- `coletado_em` DATETIME
- `ttl_horas` INTEGER
- UNIQUE(`tipo`, `marca_id`, `modelo_id`, `ano_id`)

### 5.5 Decisões importantes do modelo

- **Snapshot JSON em `vehicles`, `simulations.rules_snapshot_json`, `proposals.snapshot_json`** garante reproduzibilidade ao longo dos anos.
- `amortization_rows` materializada (não recalculada) evita drift de arredondamento.
- `indicators_history` com UNIQUE permite upsert idempotente diário.
- `extraordinary_amortizations` em separado preserva cronograma original e permite reverter.
- `audit_log.diff_json` cobre o requisito "logs de alterações" sem versionar cada tabela.
- `fipe_cache` com TTL reduz dependência de rede (FIPE muda mensalmente).

---

## 6. Core financeiro

### 6.1 Base — `money.py`

```python
from decimal import Decimal, getcontext, ROUND_HALF_UP
getcontext().prec = 28

CENTAVO  = Decimal("0.01")
PCT_DEC  = Decimal("0.0001")
TAXA_DEC = Decimal("0.00000001")

def quantize_brl(v: Decimal) -> Decimal:
    return v.quantize(CENTAVO, rounding=ROUND_HALF_UP)
```

Política de arredondamento: **half-up** em 2 casas para R$. Resíduo do arredondamento do cronograma vai **integralmente na última parcela**, garantindo saldo devedor zero exato.

### 6.2 Tabela Price com dias corridos — `price_table.py`

Modelo de capitalização exponencial fracionada (convenção BACEN/CCB):

- `i_m` = taxa mensal nominal (fração)
- `i_d = (1 + i_m)^(1/30) − 1` = taxa diária equivalente
- `d1` = dias entre liberação e primeiro vencimento
- `n` = número de parcelas (intervalos de 30 dias após `d1`)

**Parcela fixa:**

```
PMT = PV · (1+i_d)^d1 · (i_m · (1+i_m)^(n-1)) / ((1+i_m)^n − 1)
```

Quando `d1 = 30`, reduz-se à Tabela Price clássica `PMT = PV · i · (1+i)^n / ((1+i)^n − 1)`.

**Cronograma:**
- Parcela 1: `juros = PV · ((1+i_d)^d1 − 1)`; `amortização = PMT − juros`; `saldo = PV − amortização`
- Parcelas 2..n−1: `juros = saldo · i_m`; `amortização = PMT − juros`
- Parcela n: força saldo → 0; resíduo em `ajuste_arredondamento`

**Saída:**
```python
@dataclass
class Schedule:
    rows: list[ScheduleRow]
    pmt: Decimal
    total_pago: Decimal
    total_juros: Decimal
    saldo_residual: Decimal     # 0 após ajuste
```

### 6.3 IOF veículo — `iof.py`

Regulamento: Decreto 6.306/2007. Percentuais ficam em `business_rules`.

- **Fixo**: 0,38% × valor financiado
- **Diário**: 0,0082% × min(dias até vencimento da parcela, 365), aplicado sobre a amortização daquela parcela
- **Total** = fixo + Σ diário por parcela

**Fórmula:**
```
IOF_fixo    = 0.0038 × valor_financiado
IOF_diario  = Σ_k [ amortização_k × 0.000082 × min(dias_até_venc_k, 365) ]
IOF_total   = IOF_fixo + IOF_diario
```

**Circularidade quando incorporado ao principal** — resolvida por iteração:
```
PV₀ = valor_veículo − entrada + tarifas_incluídas
PV_{n+1} = PV₀ + IOF(PV_n, cronograma(PV_n))
parar quando |PV_{n+1} − PV_n| < R$ 0,01
```
Converge em 2–3 iterações na prática.

### 6.4 CET via TIR — `cet.py`

CET é a TIR mensal do fluxo de caixa do ponto de vista do cliente:

- `t = 0`: cliente recebe (em seu favor) `valor_veículo − entrada`
- `t = d1, d1+30, ...`: cliente paga `PMT`

Encontrar `i_cet` tal que:

```
(valor_veículo − entrada) = Σ_{k=1}^{n} PMT / (1 + i_cet)^((d1 + 30(k-1))/30)
```

Resolvido com `scipy.optimize.brentq` no intervalo `[1e-6, 1.0]`.

Saída:
- `cet_mes` (Decimal, 8 casas)
- `cet_ano = (1 + cet_mes)^12 − 1`

### 6.5 Taxa sugerida por prazo — `rate_suggestions.py`

Curva configurável em `business_rules.taxa_por_prazo_curva`:

```json
[
  { "ate_meses": 24, "taxa_mensal": 0.0149 },
  { "ate_meses": 36, "taxa_mensal": 0.0169 },
  { "ate_meses": 48, "taxa_mensal": 0.0189 },
  { "ate_meses": 60, "taxa_mensal": 0.0199 },
  { "ate_meses": 72, "taxa_mensal": 0.0219 }
]
```

Comportamento: se taxa atual < sugerida, UI mostra badge amarelo com botão "usar sugerida". Não bloqueia.

### 6.6 Validações — `validators.py`

Regras configuráveis (todas em `business_rules`):
- `entrada_minima_pct` (default 20%)
- `prazo_minimo_meses` (12) / `prazo_maximo_meses` (72)
- `taxa_minima_mes` (0,5%) / `taxa_maxima_mes` (5%)
- `dias_max_carencia` (90)
- `valor_minimo_financiado` (R$ 5.000)

Cada violação retorna `ValidationIssue(level='error'|'warning', field, message)`. Errors bloqueiam; warnings exibem badge na UI.

### 6.7 Amortização extraordinária — `amortization.py`

Entrada: simulação + lista de pagamentos extras `(data, valor, modo)`.

Algoritmo:
1. Percorre cronograma original aplicando pagamento extra na data (paga juros pro-rata até a data, depois reduz saldo)
2. Modo `reduzir_prazo`: mantém PMT; recalcula quantas parcelas restantes cabem
3. Modo `reduzir_parcela`: mantém prazo; recalcula PMT para saldo restante
4. Quitação total: saldo + juros pro-rata até a data; retorna desconto vs. somar parcelas remanescentes

Resultado é um **novo cronograma persistido em paralelo** (não destrói o original).

### 6.8 Testes do core

Indispensáveis:
- **Casos conhecidos**: cronogramas de simuladores reais (Santander, Itaú, Bradesco) com mesma entrada → bate centavo a centavo
- **Property tests (hypothesis)**: para qualquer `(PV, i, n, d1)` válido, `Σ amortizações ≈ PV`, `saldo_final == 0`, `parcelas > 0`
- **Casos-borda**: `d1 = 0`, `d1 = 90`, `n = 1`, taxa próxima de 0%

---

## 7. Integrações externas

### 7.1 Padrão `ProviderChain` — `integrations/base.py`

```python
class Provider(Protocol):
    name: str
    async def fetch(self, query: Query) -> Result[Payload]: ...

class ProviderChain:
    """Tenta providers em ordem; primeiro sucesso ganha. Última opção é sempre 'manual'."""
    async def fetch(self, query) -> Result[Payload]:
        for p in self.providers:
            r = await p.fetch(query)
            if r.is_ok and validate(r.value):
                audit_log("integration_hit", provider=p.name)
                return r
            audit_log("integration_miss", provider=p.name, reason=r.error)
        return Err("all_providers_failed")
```

- HTTP: `httpx.AsyncClient`, timeout 8s
- Retry: `tenacity` 3× backoff exponencial (0.5s / 1s / 2s)
- User-Agent identificando app + versão

### 7.2 FIPE — `integrations/fipe/`

**Primário — Parallelum FIPE API**
- Base: `https://parallelum.com.br/fipe/api/v2`
- Endpoints:
  - `GET /{tipo}/brands` — `tipo` ∈ `cars`, `motorcycles`, `trucks`
  - `GET /{tipo}/brands/{brandId}/models`
  - `GET /{tipo}/brands/{brandId}/models/{modelId}/years`
  - `GET /{tipo}/brands/{brandId}/models/{modelId}/years/{yearId}`

**Fallback 1 — BrasilAPI**
- Base: `https://brasilapi.com.br/api/fipe`
- Endpoints: `/marcas/v1/{tipo}`, `/preco/v1/{codigoFipe}`
- Schema adaptado para `VehicleQuote` interno

**Fallback 2 — Manual**
- Vendedor digita tipo/marca/modelo/ano/valor; gravado com `fonte='manual'`

**Cache** — `fipe/cached.py`
- Decorator sobre provider
- TTL: 30 dias para listas, 24h para preço
- Tabela `fipe_cache`

**Schema normalizado:**
```python
@dataclass
class VehicleQuote:
    tipo: Literal["carro", "moto", "caminhao"]
    marca: str
    marca_id: str
    modelo: str
    modelo_id: str
    ano_modelo: int
    combustivel: str
    codigo_fipe: str
    valor: Decimal               # parseado de "R$ 45.230,00"
    mes_referencia: str
    fonte: str
    raw_payload: dict
```

### 7.3 Indicadores econômicos — `integrations/bacen/`

**Primário — BCB SGS**
- Base: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial=...&dataFinal=...`
- Códigos:
  - `SELIC_META`: 432 (% a.a.)
  - `SELIC_DIARIA`: 11 (% a.d.)
  - `CDI`: 12 (% a.d.)
  - `IPCA`: 433 (% a.m.)
  - `TX_BACEN_VEIC`: 20714 (taxa média mensal — crédito PF aquisição veículos)
- Retorno: `[{"data": "23/05/2026", "valor": "10.50"}, ...]`

**Fallback 1 — BrasilAPI**
- `/taxas/v1/{selic|cdi|ipca}` — só último valor

**Fallback 2 — Cache local + manual**
- Usa último valor de `indicators_history` com flag `stale`
- UI mostra badge laranja "Indicador desatualizado há X dias"
- Admin pode forçar valor manual em Configurações

**IOF** — não vem de API. Vive em `business_rules` (0,38% fixo + 0,0082%/dia). Alterado por admin se a regra mudar.

**Normalização canônica:**
```python
@dataclass
class IndicatorPoint:
    codigo: str
    data_referencia: date
    valor_fracao: Decimal        # SEMPRE em fração decimal (0.015 = 1,5%)
    unidade: Literal["pct_aa", "pct_am", "pct_ad"]
    fonte: str
```

Conversões aplicadas no adapter:
- BCB SGS retorna `"10.50"` → `Decimal("10.50") / 100`
- Detecta unidade pela série (CDI=`pct_ad`, IPCA=`pct_am`, SELIC=`pct_aa`)
- Rejeita valor fora de `[0, 1]` em fração ou `[0, 100]` em pct — loga erro

**Conversões entre unidades — `bacen/conversions.py`:**
- Mensal → anual: `(1+i_m)^12 − 1`
- Diária (252) → mensal: `(1+i_d)^21 − 1`
- Diária (252) → anual: `(1+i_d)^252 − 1`
- Anual → mensal: `(1+i_a)^(1/12) − 1`

UI sempre mostra mensal e anual lado a lado para evitar confusão.

### 7.4 Agendamento — `utils/scheduler.py`

APScheduler em background no processo NiceGUI:

| Job | Frequência | Ação |
|---|---|---|
| `update_bacen_indicators` | Diária 09:00 | Upsert em `indicators_history` |
| `prune_fipe_cache` | Diária 03:00 | Remove além do TTL |
| `backup_sqlite` | Diária 23:00 | `.backup` + zip + retenção 30 dias |
| `verify_provider_health` | A cada 6h | Ping nos providers; status na aba APIs |

Cada job:
- Loga início/fim em `audit_log` (`acao='scheduled_job'`)
- Em falha, incrementa contador; badge vermelho na aba APIs
- Falhas não travam o app

### 7.5 Aba APIs (resumo — detalhado em §8.8)

Visível para gerente/admin: status, atualizar agora, reordenar chain, habilitar/desabilitar providers, histórico das últimas 50 chamadas.

---

## 8. Fluxos das 10 abas, navegação e perfis

### Layout geral

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Logo loja]        FinacialSim — Simulador de Financiamentos             │
│                                                  [Vendedor: João] [⚙] [⎋]│
├──────────────────────────────────────────────────────────────────────────┤
│ 📋 Cadastro  📊 Dashboard  💰 Simulação  ⚖ Comparativo  ⏩ Amortização   │
│ 📈 Indicadores  ⚙ Configurações  🔌 APIs  📝 Logs  📚 Documentação        │
├──────────────────────────────────────────────────────────────────────────┤
│                       [conteúdo da aba selecionada]                      │
└──────────────────────────────────────────────────────────────────────────┘
```

Abas restritas por perfil ficam **ocultas**, não apenas desabilitadas.

### Visibilidade por perfil

| Aba | Vendedor | Gerente | Admin |
|---|:---:|:---:|:---:|
| Cadastro de clientes | ✅ | ✅ | ✅ |
| Cadastro de usuários | ❌ | ❌ | ✅ |
| Dashboard | ✅ (próprio) | ✅ (loja) | ✅ |
| Simulação | ✅ | ✅ | ✅ |
| Comparativo | ✅ | ✅ | ✅ |
| Amortização | ✅ | ✅ | ✅ |
| Indicadores (leitura) | ✅ | ✅ | ✅ |
| Indicadores (editar) | ❌ | ⚠️ valores manuais | ✅ |
| Configurações (regras) | ❌ | ⚠️ visualizar | ✅ |
| APIs | ❌ | ✅ | ✅ |
| Logs | ❌ | ✅ (próprios + equipe) | ✅ (tudo) |
| Documentação | ✅ | ✅ | ✅ |

### 8.0 Login

- Dropdown "Usuário" com avatares dos usuários ativos
- Input "PIN" (4–6 dígitos, mascarado)
- 5 tentativas erradas → bloqueio de 5 min para aquele usuário
- Após login: `audit_log("login")` e abre Dashboard

### 8.1 Cadastro

Duas sub-abas (admin vê ambas; vendedor só "Clientes"):

**Clientes**
- Tabela paginada com busca por nome/CPF
- "+ Novo cliente" → modal:
  - Toggle PF/PJ alterna campos
  - PF: nome, CPF (mod-11), RG, data nasc, profissão, renda mensal
  - PJ: razão social, CNPJ, IE, faturamento
  - Telefone, email, endereço (auto-preenchido por CEP via BrasilAPI)
  - Observações
- Edição/desativação em-place
- "→ Nova simulação para este cliente" leva para Simulação pré-preenchida

**Usuários** (admin)
- Listar, criar, alterar PIN, alterar perfil, desativar
- Última atividade

### 8.2 Dashboard

Cards superiores (KPIs do mês):
- Nº de simulações
- Nº de propostas geradas
- Ticket médio financiado
- Taxa média praticada

Gráficos:
- Distribuição de prazos (barras: 24/36/48/60/72m)
- Mix de cenários (pizza PF vs PJ ou marcas mais simuladas)
- Indicadores econômicos atuais (mini-cards: SELIC, CDI, IPCA, Tx BACEN veículos)
- Evolução do saldo devedor médio
- Simulações recentes (últimas 10, click → abrir)

Vendedor vê apenas dados próprios; gerente/admin veem toda a loja com filtro por vendedor.

### 8.3 Simulação

Layout em 3 colunas.

**Esquerda — Entrada**
1. Cliente (combobox com busca, opcional)
2. Veículo:
   - Toggle [FIPE] [Manual]
   - FIPE: dropdowns em cascata Tipo → Marca → Modelo → Ano
   - Manual: campos livres + valor
   - Card mostra valor FIPE + mês de referência
3. Valor do veículo (currency, pré-preenchido)
4. Entrada — R$ ou %, sincronizados
5. Prazo (meses) — slider 12–72 + input livre
6. Taxa mensal — badge sugerindo taxa por prazo
7. Data de liberação (default hoje)
8. Data 1° vencimento (default +30d; mostra dias de carência)
9. Tarifas (expansível): cadastro, avaliação, registro — toggle "incluir no principal"

Botão "Simular" + recálculo em tempo real ao alterar campos (debounced 400ms).

**Central — Resultado (cards)**
- Valor da parcela (destaque)
- Valor financiado / Total pago / Total de juros / % juros / CET a.m. e a.a.
- Cada card tem ícone "👁" para ocultar

**Direita — Visualizações**
- Composição da parcela (barras empilhadas juros vs amortização)
- Saldo devedor (linha decrescente)
- Tabela de amortização completa (expand, exportável CSV)

**Rodapé**
- Salvar simulação
- Gerar proposta PDF (requer cliente)
- Comparar com outra (envia para Comparativo)
- Simular amortização extra (envia para Amortização)

### 8.4 Comparativo

Duas colunas espelhadas A/B com mesmo formulário compacto. Carrega simulações salvas ou edita ao vivo.

**Linha central de diferenças:**
```
                A              ↔             B              Diferença
Taxa            1,69% a.m.                   1,49% a.m.     ▼ 0,20 p.p.
Prazo           60 meses                     48 meses       ▼ 12 meses
Entrada         R$ 12.000,00                 R$ 18.000,00   ▲ R$ 6.000,00
Parcela         R$ 1.456,32                  R$ 1.523,18    ▲ R$ 66,86
Juros totais    R$ 27.380,12                 R$ 19.111,64   ▼ R$ 8.268,48
Total pago      R$ 99.380,12                 R$ 91.111,64   ▼ R$ 8.268,48
```

Gráficos sobrepostos: evolução do saldo devedor (2 linhas), juros pagos acumulados (2 linhas).

Salvar comparativo → grava em `comparisons`.

### 8.5 Amortização extraordinária

1. Carrega simulação existente (combobox)
2. Mostra cronograma original em cinza
3. Painel "Adicionar pagamento extra": data, valor, modo (parcela ou prazo)
4. Múltiplos pagamentos em sequência
5. Botões rápidos: "Quitação total agora" | "Quitação parcial 50%"
6. Recálculo em tempo real:
   - Cronograma original (cinza) vs novo (colorido) sobrepostos
   - Cards: Economia de juros, Redução de prazo (se modo prazo), Nova parcela (se modo parcela)
7. "Salvar cenário com amortização" gera nova simulação derivada

### 8.6 Indicadores

- Cards atuais: SELIC, CDI, IPCA, Tx BACEN veículos, IOF (fixo + diário)
- Cada card: valor, data, fonte, badge "atual"/"desatualizado"
- Botão "↻ Atualizar agora" (gerente/admin)
- Gráficos série histórica 12 meses (linha)
- Tabela de conversões úteis (SELIC anual → mensal, CDI diário → anual)
- Painel "Sobreposição SELIC × Tx BACEN Veículos × Taxa praticada"

### 8.7 Configurações

Áreas (admin vê todas; gerente vê leitura em algumas):
- Geral: nome da loja, logo (upload), endereço, CNPJ — usados no PDF
- Regras de negócio: entrada mínima, prazos min/max, faixa de taxa, dias máx carência, curva taxa-por-prazo
- Tarifas: cadastro/avaliação/registro (default + habilitadas)
- IOF: percentuais fixo e diário (histórico preservado)
- Backup: trigger manual, lista de backups, restaurar de arquivo
- Aparência: tema claro/escuro, cor primária
- PDF: textos cabeçalho/rodapé, observações padrão

### 8.8 APIs

- Status por provider (verde/amarelo/vermelho) + última coleta bem-sucedida
- "Atualizar agora" por indicador
- "Testar conexão" por provider
- Toggle habilitar/desabilitar (admin)
- Histórico últimas 50 chamadas (hit/miss, latência, erro)
- Ordem da chain reordenável via drag-and-drop

### 8.9 Logs

- Tabela paginada de `audit_log` com filtros por data, usuário, ação, entidade
- Detalhe expandível por linha (mostra `diff_json` formatado)
- Exportar CSV para período selecionado
- Vendedor vê só logs próprios

### 8.10 Documentação Técnica

- Visualizador embutido dos `.md` do projeto (`guia_usuario.md`, `matematica_price.md`, `troubleshooting.md`)
- Sidebar com sumário
- Renderiza Markdown com KaTeX para fórmulas
- Search box no topo

### Navegação e estado

- `router.py` centraliza guards: cada rota declara `required_role`; tentativa por perfil inferior redireciona para Dashboard com toast
- Estado da simulação atual em `app.storage.user` (NiceGUI) — sobrevive navegação, perdido ao deslogar
- Atalhos: Ctrl+S salvar, Ctrl+P imprimir/PDF, Ctrl+Tab próxima aba (configuráveis)
- Toasts padronizados (sucesso/atenção/erro/info, 4s auto-dismiss)

---

## 9. PDF, backup, migrations, logs

### 9.1 PDF de proposta — `app/reports/` + `services/proposal_service.py`

Pipeline: dados → template Jinja2 (HTML/CSS) → WeasyPrint → PDF.

**Blocos do `proposta.html`:**
1. Cabeçalho — logo, razão social, CNPJ, endereço, telefone, código, data, validade
2. Cliente — nome, CPF/CNPJ, contato, endereço
3. Veículo — marca/modelo/ano/cor/placa (opc), valor FIPE, valor de venda, fonte FIPE + mês ref
4. Condições — valor financiado, entrada (R$ e %), prazo, taxa (a.m. e a.a.), CET (a.m. e a.a.), IOF total, tarifas detalhadas, data 1º venc
5. Resumo financeiro — parcela, total pago, total de juros, % juros (cards)
6. Cronograma completo — nº, vencimento, juros, amortização, parcela, saldo
7. Gráfico de composição da parcela — render server-side (Plotly → PNG embutido)
8. Observações — configuráveis, suportam variáveis `{cliente}`, `{vendedor}`, `{prazo}`
9. Rodapé — vendedor responsável, assinaturas, validade da proposta

CSS: paleta da loja (cor primária configurável), Inter + serif, A4 com page-break inteligente.

**Snapshot:** `proposals.snapshot_json` grava tudo usado no PDF (incluindo regras e indicadores vigentes). PDF reproduzível anos depois.

**Saída:** `data/propostas/PROP-2026-00123_NomeCliente.pdf` + path em `proposals.pdf_path`. Dispara `audit_log("proposta_gerada")` e abre no visualizador padrão do SO.

### 9.2 Backup automático — `app/data/backup.py`

- Job APScheduler diário 23:00 (configurável)
- `sqlite3.Connection.backup()` (transação-safe, não copia arquivo em uso)
- Saída: `data/backups/finacialsim_2026-05-23_2300.sqlite.gz`
- Retenção default 30 dias
- Manual: Configurações → Backup → "Backup agora" / "Restaurar de arquivo..."
- Restauração: valida com `PRAGMA integrity_check`, confirma com usuário, aplica, reaplica migrations
- Backup adicional ao fechar (`_close`)

### 9.3 Migrations — `app/data/migrations/` (Alembic)

- Versionamento incremental (`001_initial.py`, ...)
- `alembic upgrade head` automático no startup (idempotente)
- Cada aplicação loga em `audit_log("migration_applied")`
- Nunca editar migration em produção — sempre nova migration corretiva
- `001_initial.py` seed: usuário `admin` com PIN `123456` (forçado a trocar no 1º login), `business_rules` defaults, IOF regulamentado

### 9.4 Logs técnicos — `app/utils/logger.py`

- loguru centralizado
- Arquivo: `logs/finacialsim_{time:YYYY-MM-DD}.log`
- Rotação diária, retenção 30 dias, gzip após 7 dias
- Níveis: DEBUG (dev), INFO (operações), WARNING (provider miss), ERROR, CRITICAL (falhas no core)
- Formato: `{time} | {level} | {module}:{function}:{line} | {message} | {extra}`
- Sentry opcional (env `SENTRY_DSN`) para ERROR/CRITICAL
- Distinção clara de `audit_log` (negócio) vs `logger` (técnico)

---

## 10. Empacotamento, instalação e atualização

### 10.1 PyInstaller — `scripts/build_exe.py`

**Windows** (`finacialsim.exe`)
- `--onedir` (startup mais rápido que `--onefile`)
- Ícone `assets/icon.ico`
- Inclui GTK+ runtime do WeasyPrint
- Saída: `dist/FinacialSim/` → NSIS gera `FinacialSim-Setup-1.0.0.exe`
- Cria `%APPDATA%/FinacialSim/data/` no primeiro run
- Atalho desktop, registro em Add/Remove Programs

**Linux** (`finacialsim.AppImage`)
- PyInstaller `--onedir` → AppImage
- Opcional: `.deb` via fpm em release futura
- Dados em `~/.local/share/FinacialSim/data/`

**Versionamento**
- `pyproject.toml` define versão
- Embutida no binário e no rodapé do app
- `app_settings.installed_version` detecta primeira execução pós-update → dispara `alembic upgrade`

### 10.2 Scripts de instalação

**Windows — `install_windows.ps1`**
- Verifica Windows 10+ x64
- Baixa instalador da última release (modo auto)
- Executa setup silenciosamente (`/S` NSIS)
- Cria atalho e entrada no menu iniciar

**Linux — `install_linux.sh`**
- Detecta distro via `/etc/os-release`
- Instala dependências de sistema do WeasyPrint se necessário
- Baixa AppImage, marca como executável, move para `/opt/finacialsim/`
- Cria `.desktop` em `~/.local/share/applications/`

**Documentação** em `docs/INSTALACAO.md` — pré-requisitos, passo-a-passo com screenshots, troubleshooting comum.

### 10.3 Atualizações

- Checagem opcional no startup contra `https://github.com/{repo}/releases/latest`
- Versão nova → badge no topbar → modal com changelog → "Baixar e instalar"
- Desativável (lojas com internet instável)
- Atualização preserva o banco; migrations rodam após update
- Releases automatizadas via GitHub Actions (tag → build paralelo Win/Linux → publica artifacts)
- Channels `beta` e `stable` (admin escolhe em Configurações)

---

## 11. Segurança e proteção

- **PIN com bcrypt** (cost factor 12)
- **5 tentativas** erradas → lockout 5 min por usuário
- **Validação Pydantic** em todos os inputs (UI, providers, configs)
- **Validação extra** em payloads de providers (faixa de valores, tipos)
- **Audit log** com `diff_json` em toda alteração de regra, indicador, cliente, simulação
- **Backup automático** + restauração validada (`PRAGMA integrity_check`)
- **Migrations versionadas** (Alembic) — nunca editar uma migration em produção
- **Snapshot JSON** preserva o passado mesmo com mudança de regras
- **Perfis ocultam UI** — não apenas desabilitam (defense-in-depth)
- **Logs técnicos** (loguru) separados de logs de negócio (audit_log)

---

## 12. Regras de negócio resumidas

Todas configuráveis em `business_rules` por admin (versionadas em `audit_log`):

| Chave | Default | Descrição |
|---|---|---|
| `entrada_minima_pct` | 0.20 | 20% mínimo de entrada |
| `prazo_minimo_meses` | 12 | |
| `prazo_maximo_meses` | 72 | |
| `taxa_minima_mes` | 0.005 | 0,5% a.m. |
| `taxa_maxima_mes` | 0.05 | 5% a.m. |
| `dias_max_carencia` | 90 | dias entre liberação e 1º vencimento |
| `valor_minimo_financiado` | 5000 | R$ |
| `iof_fixo_pct` | 0.0038 | 0,38% |
| `iof_diario_pct` | 0.000082 | 0,0082%/dia |
| `iof_diario_max_dias` | 365 | teto por parcela |
| `taxa_por_prazo_curva` | (ver §6.5) | curva crescente |
| `backup_diario_horario` | "23:00" | |
| `backup_retencao_dias` | 30 | |
| `update_indicadores_horario` | "09:00" | |
| `fipe_cache_listas_ttl_dias` | 30 | |
| `fipe_cache_preco_ttl_horas` | 24 | |

---

## 13. Integrações futuras (arquitetura preparada, desativadas no MVP)

A camada `integrations/` e os `services/` foram desenhados para acomodar:

- **CRM** — `integrations/crm/` com providers Bling/RDStation/etc. — `client_service` exporta clientes em formato compatível
- **WhatsApp** — `integrations/whatsapp/` com Twilio/Z-API — `proposal_service.send_via_whatsapp(proposal_id, phone)` mockado
- **Geração de carnê** — `services/carne_service.py` consome `amortization_rows`
- **APIs bancárias** — `integrations/bancos/` (Santander, Itaú, BV, Bradesco) — submissão real de proposta

Cada uma fica desligada via feature flag em `app_settings`. Aba "Configurações → Integrações Futuras" exibe lista cinza com botão "Configurar (em breve)".

---

## 14. Documentação a entregar

Em `docs/`:

- `ARQUITETURA.md` — versão "viva" deste spec, ligada ao código
- `DOCUMENTACAO.md` — documentação técnica completa (referência de módulos, contratos, exemplos)
- `guia_usuario.md` — voltado para vendedores: como cadastrar cliente, simular, gerar proposta, comparar
- `matematica_price.md` — explicação detalhada da Tabela Price, IOF, CET, com derivações
- `troubleshooting.md` — problemas comuns e soluções (firewall, antivírus, GTK runtime, banco corrompido)
- `INSTALACAO.md` — instalação Windows e Linux passo-a-passo

---

## 15. Testes e qualidade

- `tests/unit/core/` — bateria completa do core financeiro (cobertura ≥ 95%)
  - Cronogramas comparados centavo a centavo com Santander/Itaú/Bradesco
  - Property tests (hypothesis) garantindo invariantes
  - Casos-borda enumerados
- `tests/unit/services/` — serviços com repositórios e providers mockados
- `tests/integration/` — fluxo completo (criar cliente → simular → gerar proposta → recuperar)
- `pytest --cov` no CI; falha se cobertura cair
- Lint: `ruff` + `mypy --strict` em `core/`

---

## 16. Fora do escopo do MVP

- CRM, WhatsApp, geração de carnê, APIs bancárias (apenas arquitetura preparada)
- Sincronização entre lojas/PCs (estratégia "híbrido com sync futuro" não foi escolhida)
- Multi-tenancy
- App mobile
- Integração contábil
- Análise de crédito automatizada (consulta SCR, Serasa)
- Sistema SAC (alternativo à Tabela Price)

Esses itens podem ser adicionados em releases futuras sem reescrita do core, graças à camadização.

---

## 17. Critérios de aceitação do MVP

- [ ] Vendedor consegue, em < 2 min, simular um financiamento partindo do veículo via FIPE e vinculando a cliente cadastrado
- [ ] Cronograma gerado bate centavo a centavo com simulador de pelo menos 1 banco brasileiro de referência para 3 casos de teste
- [ ] CET calculado bate com calculadora oficial do BCB em 5 casos de teste
- [ ] PDF de proposta abre corretamente no Adobe Reader, Foxit, e leitor padrão do Windows/Linux
- [ ] Backup diário roda e arquivo `.sqlite.gz` é válido (restauração bem-sucedida)
- [ ] Atualização de indicadores às 09:00 atualiza os 5 indicadores ou marca como `stale`
- [ ] App roda em Windows 10 e Ubuntu 22.04 a partir do instalador, sem Python instalado no host
- [ ] Vendedor com perfil "vendedor" não consegue ver as abas APIs/Configurações/Logs

---

**Próximo passo:** invocar a skill `writing-plans` para criar o plano de implementação em fases (testáveis e revisáveis em separado).
