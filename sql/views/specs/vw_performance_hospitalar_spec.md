# View Spec — vw_performance_hospitalar

## Objetivo

Centralizar a evolução operacional e financeira do hospital.

Esta view alimenta o principal gráfico do dashboard executivo.

Responsável por:

- tendência mensal;
- crescimento hospitalar;
- volume operacional;
- comportamento financeiro.

---

# Objetivo de Negócio

Responder:

> O hospital está crescendo?

E também:

- o crescimento está consistente?
- receita acompanha o volume?
- internações aumentaram?

---

# Fonte de Dados

Views dependentes:

```text
vw_kpi_atendimentos
vw_kpi_internacoes
```

---

# Granularidade

Nível:

```text
mensal
```

Chave:

```text
ano_mes
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
| total_internacoes | INT |

---

## Financeiro

| Campo | Tipo |
|--------|------|
| faturamento_total | DECIMAL |

---

## Crescimento

| Campo | Tipo |
|--------|------|
| crescimento_atendimento_pct | DECIMAL |
| crescimento_internacao_pct | DECIMAL |
| crescimento_receita_pct | DECIMAL |

---

# Visual Esperado

Tipo:

```text
Line Chart
```

Séries:

```text
Atendimentos
Internações
Faturamento
```

Máximo:

```text
3 linhas
```

---

# Dashboard Dependente

Executive Overview

Card:

```text
analise_performance_hospitalar
```

---

# Regra Analítica

Receita deve acompanhar crescimento operacional.

Desvios extremos devem parecer exceção.