# View Spec — vw_kpi_internacoes

## Objetivo

Centralizar indicadores assistenciais e operacionais de internação.

Responsável por:

- total internações
- média permanência
- custo médio internação
- mortalidade hospitalar
- tendência assistencial

---

# Fonte de Dados

Tabela fato principal:

```text
fato_internacoes
```

Dimensões:

```text
dim_tempo
dim_setor
dim_convenio
dim_leito
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

## Internações

| Campo | Tipo |
|--------|------|
| total_internacoes | INT |
| media_permanencia | DECIMAL |

---

## Financeiro

| Campo | Tipo |
|--------|------|
| custo_total | DECIMAL |
| custo_medio_internacao | DECIMAL |

---

## Qualidade

| Campo | Tipo |
|--------|------|
| mortalidade_pct | DECIMAL |

---

## Leitos

| Campo | Tipo |
|--------|------|
| tipo_leito | VARCHAR |

Valores esperados:

```text
UTI Adulto
UTI Neo
Maternidade
Enfermaria
Privativo
```

---

# Perguntas Respondidas

### A internação aumentou?

Campo:

```text
total_internacoes
```

---

### O hospital está eficiente?

Campo:

```text
media_permanencia
```

---

### O custo aumentou?

Campo:

```text
custo_medio_internacao
```

---

### A qualidade caiu?

Campo:

```text
mortalidade_pct
```

---

# Dashboards Dependentes

- Executive Overview
- Internações
- Leitos
- Financeiro