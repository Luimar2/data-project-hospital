import random
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ==========================
# MYSQL
# ==========================

DB_USER = "user"
DB_PASSWORD = "userpass"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "hospital_dw"

password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# ==========================
# CARREGAR DIMENSÕES
# ==========================

tempo_df = pd.read_sql(
    "SELECT id_tempo FROM dim_tempo",
    engine
)

pacientes_df = pd.read_sql(
    "SELECT id_paciente FROM dim_paciente",
    engine
)

leitos_df = pd.read_sql(
    "SELECT id_leito, tipo_leito FROM dim_leito",
    engine
)

# ==========================
# CONFIGURAÇÃO HOSPITAL
# ==========================

TOTAL_INTERNACOES = 21840

convenios = {
    1: 0.55,
    2: 0.30,
    3: 0.10,
    4: 0.05
}

desfechos = [
    "Alta",
    "Transferência",
    "Óbito"
]

dados = []

datas = tempo_df["id_tempo"].tolist()
pacientes = pacientes_df["id_paciente"].tolist()

for _ in range(TOTAL_INTERNACOES):

    convenio = random.choices(
        list(convenios.keys()),
        weights=convenios.values()
    )[0]

    leito = leitos_df.sample(1).iloc[0]

    tipo = leito["tipo_leito"]

    # permanência por setor
    if tipo == "UTI Adulto":
        dias = random.randint(4, 15)

    elif tipo == "UTI Neo":
        dias = random.randint(7, 30)

    elif tipo == "Maternidade":
        dias = random.randint(2, 5)

    elif tipo == "Privativo":
        dias = random.randint(2, 7)

    else:
        dias = random.randint(1, 8)

    entrada = random.choice(datas)

    alta = min(
        entrada + dias,
        max(datas)
    )

    custo = round(
        dias * random.uniform(800, 3500),
        2
    )

    desfecho = random.choices(
        desfechos,
        weights=[95, 3, 2]
    )[0]

    dados.append({
        "id_paciente":
            random.choice(pacientes),

        "id_convenio":
            convenio,

        "id_leito":
            int(leito["id_leito"]),

        "id_tempo_entrada":
            entrada,

        "id_tempo_alta":
            alta,

        "tipo_internacao":
            tipo,

        "dias_internado":
            dias,

        "custo_total":
            custo,

        "desfecho":
            desfecho
    })

df = pd.DataFrame(dados)

# backup csv
df.to_csv(
    "data/processed/fato_internacoes.csv",
    index=False
)

# mysql
df.to_sql(
    "fato_internacoes",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("fato_internacoes carregada!")
print(df.head())
print(f"Total: {len(df)}")