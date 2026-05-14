# SQL Question Registry — Executive Overview

## Objetivo

Definir a lista oficial de perguntas SQL do dashboard executivo hospitalar.

Regra do projeto:

> Uma pergunta SQL = Um card do dashboard

Objetivos:

- organização da construção no Metabase;
- evitar retrabalho;
- padronização de nomenclatura;
- separação clara entre lógica do banco e lógica visual;
- facilitar manutenção do portfólio.

---

# Ordem Oficial de Construção

Construir exatamente nesta ordem.

---

# Sprint 1 — KPIs Executivos

Objetivo:

Validar views, filtros globais e camada de KPIs.

---

## Q001 — KPI Total Atendimentos

### Nome no Metabase

`kpi_total_atendimentos`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_total_atendimentos.sql
```

### Objetivo de negócio

Exibir total de atendimentos do período selecionado.

### Fonte

`vw_kpi_atendimentos`

### Tipo visual

Number Card

### Filtros globais

- Ano
- Mês
- Convênio
- Setor

### Campos esperados

```sql
total_atendimentos
```

### Prioridade

Alta

---

## Q002 — KPI Total Internações

### Nome no Metabase

`kpi_total_internacoes`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_total_internacoes.sql
```

### Objetivo

Exibir total de internações.

### Fonte

`vw_kpi_internacoes`

### Tipo

Number Card

### Filtros

- Ano
- Mês
- Convênio
- Setor

### Campo esperado

```sql
total_internacoes
```

### Prioridade

Alta

---

## Q003 — KPI Ocupação Geral

### Nome no Metabase

`kpi_ocupacao_geral`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_ocupacao_geral.sql
```

### Objetivo

Mostrar taxa geral de ocupação hospitalar.

### Fonte

`vw_ocupacao_hospitalar`

### Tipo

Number Card

### KPI Hero

Sim

### Filtros

- Ano
- Mês
- Tipo Leito
- Setor

### Campo esperado

```sql
taxa_ocupacao
```

### Prioridade

Muito Alta

---

## Q004 — KPI Receita Total

### Nome

`kpi_receita_total`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_receita_total.sql
```

### Objetivo

Mostrar faturamento do período.

### Fonte

`vw_kpi_atendimentos`

### Tipo

Number Card

### Formatação

BRL

### Filtros

- Ano
- Mês
- Convênio

### Campo esperado

```sql
faturamento_total
```

---

## Q005 — KPI Tempo Médio Espera

### Nome

`kpi_tempo_medio_espera`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_tempo_medio_espera.sql
```

### Objetivo

Exibir eficiência operacional do atendimento.

### Fonte

`vw_kpi_atendimentos`

### Tipo

Number Card

### Unidade

Minutos

### Filtros

- Ano
- Mês
- Setor

### Campo esperado

```sql
tempo_medio_espera
```

---

## Q006 — KPI Média Permanência

### Nome

`kpi_media_permanencia`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_media_permanencia.sql
```

### Objetivo

Medir eficiência assistencial.

### Fonte

`vw_kpi_internacoes`

### Tipo

Number Card

### Unidade

Dias

### Filtros

- Ano
- Mês
- Convênio
- Setor

### Campo esperado

```sql
media_permanencia
```

---

# Sprint 2 — Hero Analytics

Objetivo:

Validar leitura executiva e tendências.

---

## Q007 — Performance Hospitalar

### Nome

`analise_performance_hospitalar`

### Arquivo SQL

```text
dashboard/metabase/analyses/analise_performance_hospitalar.sql
```

### Objetivo

Mostrar crescimento operacional e financeiro.

### Fonte

Views combinadas.

### Tipo

Line Chart

### Métricas

- atendimentos
- internações
- faturamento

### Agrupamento

Mês

### Filtros

- Ano
- Convênio
- Setor

### Prioridade

Alta

---

## Q008 — SUS vs Convênio

### Nome

`analise_sus_vs_convenio`

### Arquivo SQL

```text
dashboard/metabase/analyses/analise_sus_vs_convenio.sql
```

### Objetivo

Exibir mix de atendimento.

### Tipo

Donut

### Regra do projeto

Único donut do dashboard.

### Filtros

- Ano
- Mês

---

# Sprint 3 — Operação Hospitalar

---

## Q009 — Ocupação por Tipo de Leito

### Nome

`analise_ocupacao_por_leito`

### Arquivo SQL

```text
dashboard/metabase/analyses/analise_ocupacao_por_leito.sql
```

### Tipo

Horizontal Bar

### Objetivo

Detectar saturação operacional.

### Ordem

Maior → menor

### Filtros

- Ano
- Mês
- Tipo Leito

---

## Q010 — Tempo Espera por Setor

### Nome

`analise_tempo_espera_setor`

### Arquivo SQL

```text
dashboard/metabase/analyses/analise_tempo_espera_setor.sql
```

### Tipo

Bar Chart

### Objetivo

Identificar gargalos.

### Filtros

- Ano
- Mês
- Setor

---

# Sprint 4 — Financeiro & Qualidade

---

## Q011 — Receita Mensal

### Nome

`analise_receita_mensal`

### Arquivo SQL

```text
dashboard/metabase/analyses/analise_receita_mensal.sql
```

### Tipo

Area Chart

### Objetivo

Mostrar estabilidade financeira.

### Agrupamento

Mês

### Filtros

- Ano
- Convênio

---

## Q012 — Mortalidade Hospitalar

### Nome

`kpi_mortalidade_hospitalar`

### Arquivo SQL

```text
dashboard/metabase/kpis/kpi_mortalidade_hospitalar.sql
```

### Tipo

Number Card

### Objetivo

Indicador de qualidade assistencial.

### Unidade

%

### Filtros

- Ano
- Mês
- Setor

---

# Sprint 5 — Executive Insights

---

## Q013 — Executive Insights

### Nome

`executive_insights`

### Arquivo SQL

```text
dashboard/metabase/analyses/executive_insights.sql
```

### Tipo

Tabela simples

### Objetivo

Simular inteligência executiva.

### Exemplos

- UTI Adulto acima de 90%
- Espera reduziu 12%
- Receita SUS desacelerou

### Filtros

- Ano
- Mês

---

# Regras do Projeto

## Regra 1

Uma SQL = um card

---

## Regra 2

Toda SQL salva no projeto.

Nunca deixar apenas dentro do Metabase.

---

## Regra 3

Toda pergunta deve responder uma pergunta de negócio.

---

## Regra 4

Construir seguindo a ordem oficial.

Q001 → Q013

---

## Regra 5

Validar cada pergunta antes de montar dashboard.