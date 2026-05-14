# Blueprint Técnico — vw_kpi_atendimentos

## Objetivo

Criar a view analítica responsável pelos principais KPIs operacionais de atendimento.

Esta view alimenta:

- kpi_total_atendimentos
- kpi_receita_total
- kpi_tempo_medio_espera
- analise_performance_hospitalar
- analise_receita_mensal

---

# Fonte Principal

Tabela fato:

```text
fato_atendimentos
```

---

# Dimensões Necessárias

## Tempo

```text
dim_tempo
```

Campos necessários:

```text
id_tempo
ano
mes
data_completa
```

---

## Convênio

```text
dim_convenio
```

Campos necessários:

```text
id_convenio
tipo_convenio
```

---

## Setor

```text
dim_setor
```

Campos necessários:

```text
id_setor
nome_setor
```

---

# Join Strategy

Relacionamentos esperados:

```text
fato_atendimentos.id_tempo
→ dim_tempo.id_tempo

fato_atendimentos.id_convenio
→ dim_convenio.id_convenio

fato_atendimentos.id_setor
→ dim_setor.id_setor
```

---

# Granularidade Oficial

Nível:

```text
mensal
```

Agrupar por:

```sql
ano
mes
tipo_convenio
nome_setor
```

Motivo:

Compatibilidade com filtros globais.

---

# Métricas Calculadas

## Total atendimentos

Fórmula:

```sql
COUNT(id_atendimento)
```

Output:

```text
total_atendimentos
```

---

## Tempo médio espera

Fórmula:

```sql
AVG(tempo_espera_min)
```

Output:

```text
tempo_medio_espera
```

Arredondamento:

```sql
ROUND(valor, 1)
```

---

## Faturamento total

Fórmula:

```sql
SUM(valor_atendimento)
```

Output:

```text
faturamento_total
```

---

## Ticket médio

Fórmula:

```sql
SUM(valor_atendimento)
/
COUNT(id_atendimento)
```

Output:

```text
ticket_medio
```

---

# Campos Finais Esperados

| Campo |
|--------|
| ano |
| mes |
| ano_mes |
| tipo_convenio |
| nome_setor |
| total_atendimentos |
| tempo_medio_espera |
| faturamento_total |
| ticket_medio |

---

# Exemplo de Output Esperado

| ano_mes | convenio | setor | atendimentos | espera | faturamento |
|----------|-----------|--------|---------------|---------|--------------|
| 2025-01 | SUS | Emergência | 820 | 34.2 | 152000 |
| 2025-01 | Particular | Cardiologia | 220 | 18.1 | 98000 |

---

# Cuidados Técnicos

## Não usar SELECT *

Sempre explicitar colunas.

---

## Evitar duplicidade

Validar cardinalidade dos joins.

---

## Arredondamento

Usar:

```sql
ROUND()
```

para KPIs executivos.

---

## Null safety

Usar:

```sql
COALESCE()
```

sempre que necessário.

---

# Checklist de Validação

Antes de seguir:

- [ ] total de linhas coerente
- [ ] faturamento sem explosão
- [ ] espera média plausível
- [ ] sem duplicidade
- [ ] filtros funcionando