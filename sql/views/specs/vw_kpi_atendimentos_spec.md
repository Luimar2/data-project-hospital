# View Spec — vw_kpi_atendimentos

## Objetivo

Centralizar os principais KPIs operacionais de atendimento hospitalar.

Esta view será utilizada como base para:

- KPI total atendimentos
- KPI faturamento
- KPI ticket médio
- KPI tempo médio espera
- crescimento mensal
- tendências operacionais

---

# Fonte de Dados

Tabela fato principal:

```text
fato_atendimentos
```

Dimensões relacionadas:

```text
dim_tempo
dim_setor
dim_convenio
```

---

# Granularidade

Nível:

```text
mensal
```

Chave analítica:

```text
ano_mes
```

Exemplo:

```text
2025-01
2025-02
2025-03
```

---

# Campos Obrigatórios

## Tempo

| Campo | Tipo |
|--------|------|
| ano | INT |
| mes | INT |
| ano_mes | VARCHAR |

---

## Operação

| Campo | Tipo |
|--------|------|
| total_atendimentos | INT |
| tempo_medio_espera | DECIMAL |

---

## Financeiro

| Campo | Tipo |
|--------|------|
| faturamento_total | DECIMAL |
| ticket_medio | DECIMAL |

---

## Convênio

| Campo | Tipo |
|--------|------|
| tipo_convenio | VARCHAR |

Valores esperados:

```text
SUS
Convênio
Particular
```

---

## Crescimento

| Campo | Tipo |
|--------|------|
| crescimento_atendimento_pct | DECIMAL |

---

# Perguntas de Negócio Respondidas

### O volume de atendimento cresceu?

Campo:

```text
total_atendimentos
```

---

### O faturamento aumentou?

Campo:

```text
faturamento_total
```

---

### O hospital está mais eficiente?

Campo:

```text
tempo_medio_espera
```

---

### Como está o mix SUS x Convênio?

Campo:

```text
tipo_convenio
```

---

# Dashboards Dependentes

- Executive Overview
- Operação Hospitalar
- Financeiro