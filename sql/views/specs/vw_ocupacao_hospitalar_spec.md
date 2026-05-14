# View Spec — vw_ocupacao_hospitalar

## Objetivo

Centralizar indicadores de ocupação hospitalar.

Esta é uma das views mais importantes do projeto.

Responsável por:

- taxa ocupação geral;
- ocupação por tipo de leito;
- leitos ocupados;
- leitos disponíveis;
- pressão operacional;
- tendência de ocupação.

---

# Objetivo de Negócio

Responder rapidamente:

> O hospital está operando dentro da capacidade saudável?

Também responder:

- quais áreas estão saturadas?
- qual leito possui maior pressão?
- existe risco operacional?
- a ocupação está aumentando?

---

# Fonte de Dados

Tabela fato principal:

```text
fato_internacoes
```

Dimensões:

```text
dim_tempo
dim_leito
dim_setor
```

---

# Granularidade

Nível principal:

```text
diário
```

Motivo:

Permitir análises temporais e agregação mensal.

A view poderá ser agrupada no Metabase para:

```text
dia
semana
mês
```

---

# Estrutura Hospitalar Oficial

Capacidade instalada simulada:

| Tipo Leito | Quantidade |
|------------|------------|
| Enfermaria | 80 |
| Maternidade | 20 |
| Privativo | 10 |
| UTI Adulto | 10 |
| UTI Neo | 14 |

---

# Campos Obrigatórios

## Tempo

| Campo | Tipo |
|--------|------|
| data | DATE |
| ano | INT |
| mes | INT |
| ano_mes | VARCHAR |

---

## Leitos

| Campo | Tipo |
|--------|------|
| tipo_leito | VARCHAR |
| total_leitos | INT |
| leitos_ocupados | INT |
| leitos_disponiveis | INT |

---

## KPI Principal

| Campo | Tipo |
|--------|------|
| taxa_ocupacao | DECIMAL |

Fórmula:

```text
(leitos_ocupados / total_leitos) * 100
```

---

## Saúde Operacional

| Campo | Tipo |
|--------|------|
| status_ocupacao | VARCHAR |

Valores esperados:

```text
Saudável
Atenção
Crítico
```

Regra:

### Saudável

```text
até 80%
```

### Atenção

```text
80% até 90%
```

### Crítico

```text
acima de 90%
```

---

# Perguntas Respondidas

### O hospital está lotado?

Campo:

```text
taxa_ocupacao
```

---

### Qual área está saturada?

Campo:

```text
tipo_leito
```

---

### Existe capacidade disponível?

Campo:

```text
leitos_disponiveis
```

---

### Como está a pressão operacional?

Campo:

```text
status_ocupacao
```

---

# Dashboards Dependentes

## Executive Overview

Cards:

```text
kpi_ocupacao_geral
analise_ocupacao_por_leito
```

---

## Dashboard Internações

Cards:

```text
ocupacao_diaria
ocupacao_mensal
ocupacao_por_leito
```

---

# Regras Analíticas

## Regra 1

Nunca permitir ocupação superior a:

```text
100%
```

Mesmo em dados sintéticos.

---

## Regra 2

Toda ocupação deve respeitar:

```text
capacidade instalada
```

---

## Regra 3

UTI Adulto deve ter maior sensibilidade operacional.

Motivo:

Leito crítico.

---

## Regra 4

UTI Neo deve apresentar sazonalidade menor.

Motivo:

Menor volatilidade operacional.

---

# Visual Esperado no Dashboard

## KPI Hero

```text
87%
```

Exemplo:

```text
Taxa de Ocupação
87%
+2,3% vs mês anterior
```

---

## Ocupação por Leito

Exemplo:

```text
UTI Adulto      92%
UTI Neo         84%
Maternidade     76%
Enfermaria      68%
Privativo       52%
```

Tipo visual:

```text
Horizontal Bar
```

---

# Dependências Técnicas

Necessário relacionamento correto entre:

```text
fato_internacoes
→ dim_leito
→ dim_tempo
```

---

# Observações

Esta é uma VIEW CORE do projeto.

Qualquer erro aqui impacta:

- Executive Overview
- Dashboard Internações
- Storytelling do hospital
- Hero KPI