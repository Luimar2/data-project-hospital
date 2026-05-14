# View Spec — vw_receita_mensal

## Objetivo

Centralizar evolução financeira do hospital.

Responsável por:

- receita mensal;
- tendência financeira;
- crescimento do faturamento.

---

# Objetivo de Negócio

Responder:

> O hospital está financeiramente saudável?

---

# Fonte

Dependência:

```text
vw_kpi_atendimentos
```

---

# Granularidade

Nível:

```text
mensal
```

---

# Campos Obrigatórios

| Campo | Tipo |
|--------|------|
| ano | INT |
| mes | INT |
| ano_mes | VARCHAR |
| faturamento_total | DECIMAL |
| ticket_medio | DECIMAL |

---

# Visual Esperado

Tipo:

```text
Area Chart
```

Não usar:

```text
Stacked Area
```

---

# Dashboard Dependente

Executive Overview

Card:

```text
analise_receita_mensal
```

---

# Regra Analítica

Receita deve demonstrar leve crescimento ao longo do tempo.

Evitar oscilações irreais nos dados sintéticos.