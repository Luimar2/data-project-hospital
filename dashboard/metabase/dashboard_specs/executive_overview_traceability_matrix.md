# Executive Overview — Traceability Matrix

## Objetivo

Mapear cada card do dashboard executivo para sua origem analítica.

Essa matriz responde:

- qual view alimenta o card;
- qual campo utilizar;
- qual visual usar;
- se já está pronto;
- se precisa SQL no Metabase;
- se precisa nova VIEW.

---

# ROW 1 — Executive KPIs

| Card | Fonte | Campo | Tipo Visual | Status | Observação |
|------|--------|--------|--------------|---------|-------------|
| Total Atendimentos | vw_kpi_atendimentos | total_atendimentos | Number | ✅ | pronto |
| Total Internações | vw_kpi_internacoes | total_internacoes | Number | ✅ | pronto |
| Taxa Ocupação | vw_ocupacao_hospitalar | taxa_ocupacao | Number | 🔍 | validar granularidade |
| Receita Total | vw_kpi_atendimentos | faturamento_total | Number | ✅ | pronto |
| Tempo Médio Espera | vw_kpi_atendimentos | tempo_medio_espera | Number | ✅ | pronto |
| Média Permanência | vw_kpi_internacoes | media_permanencia | Number | ✅ | pronto |

---

# ROW 2 — Hero Analytics

| Card | Fonte | Campo | Tipo Visual | Status | Observação |
|------|--------|--------|--------------|---------|-------------|
| Performance Hospitalar | nova view | múltiplos | Line Chart | ⚠️ | criar vw_performance_hospitalar |
| SUS vs Convênio | SQL Metabase | atendimentos_sus / atendimentos_convenio | Donut | ⚠️ | pode derivar da view atual |

---

# ROW 3 — Pressão Operacional

| Card | Fonte | Campo | Tipo Visual | Status | Observação |
|------|--------|--------|--------------|---------|-------------|
| Ocupação por Leito | vw_ocupacao_hospitalar | taxa_ocupacao | Horizontal Bar | 🔍 | validar colunas disponíveis |
| Espera por Setor | nova query Metabase | tempo_medio_espera | Bar Chart | ⚠️ | provável SQL direto na fato |

---

# ROW 4 — Financeiro & Qualidade

| Card | Fonte | Campo | Tipo Visual | Status | Observação |
|------|--------|--------|--------------|---------|-------------|
| Receita Mensal | vw_kpi_atendimentos | faturamento_total | Area Chart | ✅ | não precisa nova view |
| Mortalidade Hospitalar | vw_kpi_internacoes | taxa_mortalidade | Number | ✅ | pronto |

---

# ROW 5 — Executive Insights

| Card | Fonte | Campo | Tipo Visual | Status | Observação |
|------|--------|--------|--------------|---------|-------------|
| Executive Insights | SQL Metabase | regras condicionais | Table/Text | ⚠️ | criar no final |

---

# Resumo Técnico

## Já pronto

```text
vw_kpi_atendimentos
vw_kpi_internacoes
vw_ocupacao_hospitalar
```

---

## Precisará criar

```text
vw_performance_hospitalar
```

---

## SQL no Metabase

```text
SUS vs Convênio
Espera por setor
Executive Insights
```

---

## Não precisa criar nova view

```text
Receita mensal
Mortalidade
Receita total
Tempo espera
Média permanência
```

---

# Ordem Recomendada

1. Auditar vw_ocupacao_hospitalar
2. Criar vw_performance_hospitalar
3. Construir Sprint 1 no Metabase
4. Construir Hero Analytics
5. Operação Hospitalar
6. Financial Layer
7. Executive Insights