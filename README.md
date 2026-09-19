# Hospital Data Project

Projeto de análise de dados hospitalares desenvolvido com foco em **engenharia e análise de dados, modelagem dimensional e Business Intelligence**.

O projeto utiliza dados sintéticos para simular a operação de um hospital de médio porte e construir um fluxo completo de dados, desde a geração e preparação dos dados até sua disponibilização em banco de dados e visualização no Metabase.

## Objetivo

Construir um projeto prático de dados que permita trabalhar, de forma integrada, conceitos de:

* geração e preparação de dados;
* modelagem de banco de dados;
* SQL;
* Python para manipulação e geração de dados;
* modelagem dimensional;
* indicadores hospitalares;
* análise de dados;
* Business Intelligence;
* construção de dashboards no Metabase;
* auditoria e validação da qualidade dos dados.

O projeto também serve como ambiente de estudo e portfólio para demonstrar um fluxo de trabalho de análise de dados aplicado a um contexto empresarial.

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

## Tecnologias

* **Python**
  * Pandas
  * NumPy
  * Faker
  * SQLAlchemy
  * PyMySQL
  * python-dotenv
* **MySQL**
* **Metabase**
* **SQL**
* **Git**

## Estrutura do projeto

```text
data-project-hospital/
├── dashboard/
│   └── metabase/
│       ├── analyses/
│       ├── dashboard_specs/
│       ├── kpis/
│       └── screenshots/
│
├── data/
│   ├── processed/
│   └── raw/
│
├── logs/
│
├── markdowns/
│
├── notebooks/
│
├── scripts/
│   ├── __pycache__
│   ├── load/
│   ├── synthetic/
│   ├── transform/
│   └── main.py
│
├── sql/
│   ├── queries/
│   ├── schemas/
│   ├── seeds/
│   └── views/
│
├── venv/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Dados

Os dados utilizados no projeto são **sintéticos** e foram desenvolvidos especificamente para representar um cenário hospitalar.

O conjunto de dados contempla informações relacionadas a:

* pacientes;
* atendimentos;
* internações;
* leitos;
* setores;
* convênios;
* calendário e períodos de análise.

Os arquivos gerados em formato CSV são mantidos no projeto para permitir rastreabilidade, reprodução e inspeção dos dados utilizados nas etapas posteriores.

## Banco de dados

Os dados são organizados em um modelo dimensional no MySQL, com tabelas de dimensão e fatos.

Entre os principais objetos estão:

* `dim_tempo`
* `dim_setor`
* `dim_convenio`
* `dim_paciente`
* `dim_leito`
* `fato_atendimentos`
* `fato_internacoes`

O banco também possui views destinadas à disponibilização de indicadores e informações consolidadas para análise e visualização.

## Scripts

Os scripts Python estão organizados conforme sua finalidade:

### `scripts/synthetic/`

Responsável pela geração dos dados sintéticos utilizados no projeto.

### `scripts/transform/`

Contém rotinas relacionadas à transformação e preparação dos dados.

### `scripts/load/`

Contém rotinas relacionadas à carga dos dados no banco de dados.

### `scripts/main.py`

Arquivo de entrada atualmente presente na estrutura do projeto. Seu papel definitivo dentro do fluxo será documentado após a revisão final dos scripts.

## SQL

A pasta `sql/` concentra os objetos e consultas utilizados na construção e análise do banco de dados.

### `schemas/`

Scripts de criação das tabelas e estruturas do banco.

### `seeds/`

Dados iniciais utilizados para povoar tabelas de referência, como setores e convênios.

### `views/`

Views utilizadas para consolidação e disponibilização dos indicadores analíticos.

### `queries/`

Consultas SQL utilizadas durante as análises.

## Dashboard

A camada de Business Intelligence utiliza o **Metabase**.

Os materiais relacionados ao dashboard estão organizados em:

```text
dashboard/metabase/
├── analyses/
├── dashboard_specs/
├── kpis/
└── screenshots/
```

Essa estrutura separa as definições e materiais auxiliares utilizados durante o desenvolvimento dos dashboards.

## Ambiente de desenvolvimento

O projeto utiliza um ambiente virtual Python próprio:

```text
venv/
```

As dependências do projeto estão registradas em:

```text
requirements.txt
```

As credenciais de acesso ao banco de dados são mantidas em um arquivo `.env`, que não é versionado pelo Git.

As variáveis utilizadas atualmente são:

```text
MYSQL_USER
MYSQL_PASSWORD
MYSQL_HOST
MYSQL_PORT
MYSQL_DATABASE
```

## Status

O projeto encontra-se em desenvolvimento.

A estrutura, os scripts, o modelo de dados e os dashboards estão sendo revisados e validados progressivamente antes da consolidação da versão final.

