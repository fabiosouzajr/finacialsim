Você é um arquiteto sênior de soluções financeiras, especialista em matemática financeira bancária,  Python e integração com APIs financeiras.

Sua tarefa é gerar um sistema profissional completo de simulação de financiamento de veículos para uso interno de uma loja de carros no Brasil.


# OBJETIVO PRINCIPAL

De acordo com os requisitos abaixo sugira uma arquitetura ideal para a solução que seja intuitiva e modular capaz de simular financiamentos automotivos utilizando metodologia bancária real baseada na Tabela Price, juros compostos e cálculo financeiro muito próximo do utilizado por bancos e financeiras brasileiras.

## REQUISITOS DE ARQUITETURA

O sistema deverá:

* ser altamente visual, intuitivo para usuários leigos
* capaz de ser facilmente instalado
* funcionar em multiplas plataformas
* fazer o máximo uso de biblotecas consolidadas para facilitar e encurtar tempo de desenvolvimento e manutenção
* use um banco de dados simples
* preparado para expansão futura



---

# REQUISITOS FUNCIONAIS

## Cadastro de clientes

O sistema deverá permitir um cadastro de clientes que será vinculado a simulações. Essas simulações podem virar propostas personalizadas com os dados do cliente.

---

## Entrada de dados do veículo

O sistema deverá permitir:

* Digitação manual do valor do veículo
* Campo para valor da entrada
* Cálculo automático do percentual da entrada
* Campo para taxa de juros mensal
* Campo para prazo em meses (campo livre)
* Campo para primeiro vencimento
* Simulação baseada em dias corridos

---

# TABELA FIPE

Implementar integração com API FIPE.

O Fluxo desejado deverá ser semelhante ao implementado pela pagina da fipe em que:

1. Usuário seleciona atraves de filtros:

   Tipo de veiculo:
   * carro / motos / caminhões

   Marca:
   * De acordo com o tipo de veiculo selecionado, será exibida lista de marcas

   Modelo:
   * De acordo com o tipo de marca selecionado, será exibida lista de modelos

   Ano:
   * De acordo com o tipo de modelo selecionado, será exibida lista anos


2. Sistema busca automaticamente:

   * valor FIPE atualizado

A integração poderá utilizar:

* APIs gratuitas
* Módulos e biblotecas Python
* scraping, se necessário

Sempre criar fallback manual caso a API falhe e implementar validação de dados.

---

# INDICADORES ECONÔMICOS AUTOMÁTICOS

Criar seção dedicada para atualização automática dos seguintes indicadores:

* SELIC
* CDI
* IPCA
* Taxa média de financiamento BACEN
* IOF atualizado

Esses dados deverão ser atualizados automaticamente pela internet. Atentar para taxas ao mês e ao ano e formato númerico (0,015 vs 1,5%). Implementar validação.

Permitir:

* atualização manual
* atualização automática
* fallback em caso de falha

---

# SISTEMA DE FINANCIAMENTO

Utilizar:

* Fórmula exata da Tabela Price
* Juros compostos
* Arredondamento bancário real
* Cálculo por dias corridos
* Primeiro vencimento variável
* Simulação próxima do comportamento bancário real

Implementar:

* aumento automático sugerido da taxa conforme aumento do prazo
* validação de entrada mínima obrigatória
* regras configuráveis

---

# FUNCIONALIDADES DA SIMULAÇÃO

O sistema deverá exibir:

* valor da parcela
* valor financiado
* total pago
* total de juros
* percentual de juros
* CET estimado
* cronograma completo de amortização
* saldo devedor mês a mês
* composição da parcela
* juros pagos
* amortização paga

Todos os elementos deverão possuir opção de ocultar/exibir.

---

# COMPARAÇÃO ENTRE CENÁRIOS

Implementar comparação entre 2 financiamentos simultaneamente.

Comparar:

* taxa
* prazo
* entrada
* parcela
* juros totais
* total pago

Mostrar diferenças visuais.

---

# AMORTIZAÇÃO ANTECIPADA

Implementar simulação de:

* amortização extraordinária
* quitação parcial
* quitação total

Permitir ao usuário escolher:

* redução de parcela
* redução de prazo

Recalcular automaticamente toda a tabela.

---

# INTERFACE E UX

A interface deve ser:

* extremamente intuitiva
* amigável para vendedores
* rápida de operar
* altamente visual
* com aparência profissional

Utilizar:

* cores
* cards
* indicadores visuais
* gráficos
* validações visuais
* dropdowns
* menus suspensos
* campos destacados
* feedback visual para erros

Evitar aparência excessivamente técnica.

---

# DASHBOARD

Criar dashboard executivo contendo:

* resumo do financiamento
* impacto da entrada
* comparação entre prazos
* composição das parcelas
* gráficos financeiros
* indicadores econômicos atuais

Criar gráficos para:

* composição da parcela
* evolução do saldo devedor
* impacto da entrada
* comparação de cenários

---

# SEÇÕES DO APLICATIVO

Separar em múltiplas abas organizadas:

1. Cadastro
2. Dashboard
3. Simulação
4. Comparativo
5. Amortização
6. Indicadores
7. Configurações
8. APIs
9. Logs
10. Documentação Técnica

---

# SEGURANÇA E PROTEÇÃO

Implementar:

* Sistema de migração
* validação de entradas e dados obtidos por APIs
* tratamento de erros
* logs de alterações
* backup automático
* versionamento básico

Criar níveis de acesso:

* vendedor
* gerente
* administrador

Ocultar áreas técnicas conforme perfil.

---

# AUTOMAÇÕES

Gerar:
* scripts Python auxiliares
* automações
* funções customizadas
* documentação de instalação
* geração de PDF de proposta

---

# DOCUMENTAÇÃO

Gerar documentação extremamente detalhada contendo:

* arquitetura do applicativo
* descrição das seções
* explicação das fórmulas
* explicação matemática da Tabela Price
* explicação dos cálculos bancários
* instruções de manutenção
* instruções de atualização
* documentação técnica
* guia do usuário
* troubleshooting

---

# INTEGRAÇÕES FUTURAS

Preparar arquitetura para futura integração com:

* CRM
* WhatsApp
* geração automática de carnê
* APIs bancárias

Mesmo que inicialmente desativadas.

---

# FORMATAÇÃO E REGIONALIZAÇÃO

Utilizar padrão brasileiro:

* idioma PT-BR
* moeda R$
* formato R$ 10.000,00
* separador decimal brasileiro
* nomenclaturas brasileiras

---

# COMPATIBILIDADE

Prioridade máxima:

* Windows (instalavel localmente)
* Linux (instalavel localmente)

---

# QUALIDADE TÉCNICA

O sistema deverá ser:

* modular
* escalável
* organizado
* comentado
* profissional
* preparado para manutenção futura

---

# ENTREGA ESPERADA

Você deverá gerar os seguintes arquivos `.md`:

## `ARQUITETURA.md` contendo:
* Detalhamento do aplicativo com objetivos e capacidades
* Arquitetura completa do applicativo
* Lista de módulos e bibliotecas Python, bem como scripts auxiliares
* Integrações com APIs
* Detalhamento do esqueleto do aplicativo (diretorios e arquivos) explicando funções.
* Layout sugerido das seções
* Dashboard
* Gráficos
* Regras de negócio


## `DOCUMENTAÇÃO.md` contendo:
* Documentação técnica completa
* Guia de uso
* Explicação matemática
* Sistema de proteção
* Estratégia de atualização automática
* Plano de expansão futura

---

# IMPORTANTE

* Não simplifique os cálculos financeiros.
* Utilize práticas próximas às utilizadas por bancos brasileiros.
* Priorize precisão financeira.
* Priorize usabilidade para vendedores.
* Estruture a solução como um sistema profissional real.
* Gere código limpo, modular e documentado.
* Explique todas as decisões técnicas importantes.
