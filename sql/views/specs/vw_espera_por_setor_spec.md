# View Spec — vw_espera_por_setor

## Objetivo

Centralizar eficiência operacional do atendimento.

Responsável por:

- tempo médio de espera;
- gargalos;
- eficiência por setor.

---

# Objetivo de Negócio

Responder:

> Onde existem gargalos operacionais?

---

# Fonte

Tabela fato:

```text
fato_atendimentos
```

Dimensões:

```text
dim_setor
dim_tempo
```

---

# Granularidade

Nível:

```text
mensal por setor
```

---

# Campos Obrigatórios

| Campo | Tipo |
|--------|------|
| ano | INT |
| mes | INT |
| ano_mes | VARCHAR |
| setor | VARCHAR |
| tempo_medio_espera | DECIMAL |
| total_atendimentos | INT |

---

# Setores Esperados

```text
Emergência
Cardiologia
Obstetrícia
Internação
Centro Cirúrgico
```

---

# Visual Esperado

Tipo:

```text
Horizontal Bar
```

Ordem:

```text
Maior → menor espera
```

---

# Dashboard Dependente

Executive Overview

Card:

```text
analise_tempo_espera_setor
```

---

# Regra Analítica

Emergência deve apresentar maior variabilidade.

Centro cirúrgico tende a menor espera.