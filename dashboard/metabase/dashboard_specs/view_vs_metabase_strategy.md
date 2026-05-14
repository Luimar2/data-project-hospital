# Strategy — MySQL Views vs Metabase SQL

## Objetivo

Definir a arquitetura oficial do projeto para separar:

- lógica analítica;
- cálculos de negócio;
- camada visual;
- responsabilidade do Metabase.

Princípio do projeto:

> Metabase não substitui modelagem analítica.

---

# Regra Principal

## MySQL

Responsável por:

- regras de negócio;
- agregações;
- KPIs;
- joins complexos;
- métricas hospitalares;
- cálculos reutilizáveis.

---

## Metabase

Responsável por:

- visualização;
- filtros;
- comparações simples;
- layout;
- interatividade.

---

# O que deve ficar em VIEW no MySQL

Regra:

Se o cálculo for importante para o negócio ou reutilizável → VIEW.

---

## KPI Atendimentos

### Vai para VIEW

Arquivo:

```text
sql/views/vw_kpi_atendimentos.sql
```

Responsável por:

- total atendimentos
- ticket médio
- faturamento
- tempo médio espera
- crescimento mensal

Motivo:

Alta reutilização.

Usado em vários dashboards.

---

## KPI Internações

### Vai para VIEW

Arquivo:

```text
sql/views/vw_kpi_internacoes.sql
```

Responsável por:

- total internações
- média permanência
- custo médio
- mortalidade
- crescimento

Motivo:

Métrica hospitalar central.

---

## Ocupação Hospitalar

### Vai para VIEW

Arquivo:

```text
sql/views/vw_ocupacao_hospitalar.sql
```

Responsável por:

- ocupação geral
- ocupação por leito
- leitos disponíveis
- ocupação diária

Motivo:

Lógica hospitalar crítica.

---

## Performance Hospitalar Mensal

### Vai para VIEW

Arquivo:

```text
sql/views/vw_performance_hospitalar.sql
```

Responsável por:

- atendimentos mensal
- internações mensal
- faturamento mensal

Motivo:

Hero chart do dashboard.

Não recalcular no Metabase.

---

## SUS vs Convênio

### Vai para VIEW

Arquivo:

```text
sql/views/vw_mix_convenios.sql
```

Responsável por:

- SUS
- Convênio
- Particular
- percentuais

Motivo:

Reutilização alta.

---

## Espera por Setor

### Vai para VIEW

Arquivo:

```text
sql/views/vw_espera_por_setor.sql
```

Responsável por:

- tempo espera
- ranking setores

Motivo:

Operacional.

---

## Receita Mensal

### Vai para VIEW

Arquivo:

```text
sql/views/vw_receita_mensal.sql
```

Responsável por:

- faturamento mensal
- tendência financeira

Motivo:

Reuso.

---

## Executive Insights

### Vai para SQL no Metabase

Motivo:

Lógica mais experimental.

Pode mudar bastante.

Não precisa persistir inicialmente.

---

# O que NÃO deve ficar no banco

## Comparação vs mês anterior

Deixar no Metabase.

Exemplo:

```text
+4,2%
vs mês anterior
```

Motivo:

Camada visual.

---

## Formatação monetária

Metabase.

---

## Cor condicional

Metabase.

---

## Filtros interativos

Metabase.

---

## Ordenação visual

Metabase.

---

# Arquitetura Final

```text
RAW DATA
   ↓
FACT TABLES
   ↓
DIMENSIONS
   ↓
ANALYTICAL VIEWS (MYSQL)
   ↓
METABASE QUESTIONS
   ↓
DASHBOARD
```

---

# Benefícios da arquitetura

### Performance

Mais rápido.

---

### Organização

SQL centralizada.

---

### Portfólio forte

Demonstra:

- modelagem dimensional
- SQL analytics
- BI architecture
- dashboard design

---

# Regra Oficial do Projeto

Se a lógica pode ser reutilizada:

> VIEW

Se é apenas visual:

> METABASE