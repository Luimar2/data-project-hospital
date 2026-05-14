# Dashboard Spec — Executive Overview

## Objetivo do dashboard

Responder rapidamente:

> “O hospital está saudável operacionalmente e financeiramente?”

Tempo ideal de leitura:

```
15–30 segundos
```

Público-alvo:

```
Diretoria
Gestores hospitalares
Administrativo
```

Storytelling:

```
1. Status atual
2. Tendência
3. Pressão operacional
4. Resultado financeiro
5. Qualidade assistencial
6. Alertas
```

---

# GRID OFICIAL

No Metabase vamos trabalhar pensando em:

```
Desktop widescreen
16:9
```

Estrutura:

```
12 colunas
```

Mesmo que o Metabase abstraia isso, pensar assim ajuda MUITO.

---

# HEADER

## Componente

Dashboard Header

Posição:

```
topo
```

Título:

```
Hospital Executive Overview
```

Subtítulo:

```
Indicadores estratégicos hospitalares
2025–2026
```

---

## Filtros globais

Posição:

```
top-right
```

### Filtro 1

Nome:

```
Ano
```

Tipo:

Dropdown

Fonte:

`dim_tempo`

---

### Filtro 2

```
Mês
```

---

### Filtro 3

```
Convênio
```

Valores:

```
Todos
SUS
Convênio
Particular
```

---

### Filtro 4

```
Setor
```

---

### Filtro 5

```
Tipo Leito
```

---

# ROW 1 — KPI Executive Layer

Objetivo:

Mostrar o estado do hospital.

Grid:

```
3 colunas x 2 linhas
```

Altura:

Pequena/média.

---

## CARD 01

### Nome

```
kpi_total_atendimentos
```

### Pergunta de negócio

```
O volume assistencial cresceu?
```

### Fonte

`vw_kpi_atendimentos`

### Tipo visual

**Number**

### Exibição

```
6521
+4,2%
vs mês anterior
```

### Cor

Azul principal.

---

## CARD 02

```
kpi_total_internacoes
```

Pergunta:

```
Internações cresceram?
```

Tipo:

Number.

---

## CARD 03 (Hero KPI)

### Nome

```
kpi_ocupacao_geral
```

### Pergunta

```
Estamos operando acima da capacidade ideal?
```

### Tipo

Number Card.

### Tamanho

**1.25x maior**

Mais destaque visual.

### Regra de cor

```
<80% verde
80–90% laranja
>90% vermelho
```

---

## CARD 04

```
kpi_receita_total
```

Formato:

Moeda brasileira.

```
R$ 4,8M
```

---

## CARD 05

```
kpi_tempo_medio_espera
```

Formato:

```
34 min
```

Cor semântica.

---

## CARD 06

```
kpi_media_permanencia
```

Formato:

```
4,7 dias
```

---

## Layout visual real

```
┌──────────┬──────────┬────────────┐
│Atendim.  │Internaç. │Ocupação    │
├──────────┼──────────┼────────────┤
│Receita   │Espera    │Permanência │
└──────────┴──────────┴────────────┘
```

---

# ROW 2 — Hero Analytics

Objetivo:

Mostrar tendência do hospital.

---

## CARD 07 (Hero Chart)

### Nome

```
analise_performance_hospitalar
```

### Pergunta

```
O hospital está crescendo?
```

### Tipo

**Line Chart**

### Grid

```
70%
```

### Métricas

- atendimentos
- internações
- faturamento

### Agrupamento

Mês.

### Regra

Máximo:

```
3 linhas
```

---

## CARD 08

### Nome

```
analise_sus_vs_convenio
```

### Tipo

Donut.

### Grid

```
30%
```

### Regra

Único donut do dashboard.

---

Layout:

```
┌──────────────────────────┬──────────┐
│ Performance Hospitalar   │ SUS Conv │
└──────────────────────────┴──────────┘
```

---

# ROW 3 — Pressão Operacional

Objetivo:

Detectar gargalos.

---

## CARD 09

```
analise_ocupacao_por_leito
```

Tipo:

Horizontal Bar.

Pergunta:

```
Quais áreas estão saturadas?
```

---

## CARD 10

```
analise_tempo_espera_setor
```

Pergunta:

```
Onde há gargalo operacional?
```

---

Layout:

```
┌──────────────────────────┬──────────┐
│ Ocupação de Leitos       │ Espera   │
└──────────────────────────┴──────────┘
```

---

# ROW 4 — Financeiro + Qualidade

---

## CARD 11

```
analise_receita_mensal
```

Tipo:

Area chart.

Pergunta:

```
Receita está estável?
```

---

## CARD 12

```
kpi_mortalidade_hospitalar
```

Tipo:

Number Card.

Formato:

```
2,1%
Dentro baseline
```

---

# ROW 5 — Executive Insights

Objetivo:

Simular inteligência executiva.

---

## CARD 13

Nome:

```
executive_insights
```

Tipo:

Tabela simples.

Altura:

Baixa.

Exemplo:

```
🟡 UTI Adulto acima de 90%

🟢 Espera reduziu 12%

🔴 Receita SUS desacelerou
```

---

# Ordem de construção recomendada

Agora entra a parte prática.

Não tente montar tudo.

Faça nesta ordem:

### Sprint 1

KPIs (row 1)

```
card 1 → 6
```

---

### Sprint 2

Hero chart + SUS vs convênio

```
card 7 → 8
```

---

### Sprint 3

Operação

```
card 9 → 10
```

---

### Sprint 4

Financeiro + qualidade

```
card 11 → 12
```

---

### Sprint 5

Insights + polish visual

```
card 13
```