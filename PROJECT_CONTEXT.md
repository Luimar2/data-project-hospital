# Projeto: Data Warehouse Hospitalar

## Objetivo do Projeto

Projeto de BI hospitalar para construção de dashboard executivo com indicadores hospitalares utilizando dados sintéticos consistentes.

Foco:
- Gestão hospitalar
- Indicadores operacionais
- Indicadores financeiros
- Ocupação hospitalar
- Visualização executiva

Stack utilizada:
- Python
- MySQL 8 (Docker)
- Metabase
- SQL
- Pandas
- SQLAlchemy
- Docker Compose

---

## Estrutura do Projeto

```
text
data-project/
├── dashboard
├── data
│   ├── external
│   ├── processed     # CSVs tratados
│   ├── raw           # PDFs e dados brutos
│   └── staging
├── docker
│   └── docker-compose.yml
├── logs
├── notebooks
├── README.md
├── scripts
│   ├── extract       # extração de PDF
│   ├── load          # carga no MySQL
│   ├── main.py
│   ├── synthetic
│   └── transform     # limpeza
├── site
├── sql
│   ├── queries
│   ├── schemas
│   ├── seeds
│   └── views
└── venv
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    └── pyvenv.cfg
```

---

## Contexto Hospitalar Simulado

Hospital de médio porte.

Estrutura:

- 80 leitos enfermaria
- 20 leitos maternidade
- 10 leitos privativos
- 10 leitos UTI adulto
- 14 leitos UTI Neo
- 8 salas centro cirúrgico
- 4 salas PPP (pré-parto)
- Urgência e emergência 24h
- Pronto Atendimento 24h
- Internação
- Cardiologia
- Obstetrícia
- Cirurgias eletivas
- Convênios + SUS

Volume operacional:

- ~6500 atendimentos/mês
- ~910 internações/mês
- Dados de 2025–2026

---

## Modelagem Dimensional (Star Schema)

### Dimensões

- dim_tempo
- dim_setor
- dim_convenio
- dim_paciente
- dim_leito

### Fatos

- fato_atendimentos
- fato_internacoes

### Views Analíticas

- vw_ocupacao_hospitalar
- vw_kpi_atendimentos
- vw_kpi_internacoes

---

## Indicadores já disponíveis

### Atendimento

- Total atendimentos
- Tempo médio espera
- Ticket médio
- Faturamento
- SUS vs Convênio
- Sazonalidade mensal

### Internação

- Total internações
- Média permanência
- Custo médio internação
- Custo hospitalar total
- Mortalidade hospitalar
- SUS vs Convênio

### Ocupação

- Taxa ocupação por tipo leito
- Leitos ocupados
- Leitos disponíveis
- Ocupação diária
- UTI adulto
- UTI Neo
- Maternidade

---
