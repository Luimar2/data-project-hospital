import random
import pandas as pd
from sqlalchemy import create_engine, text
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
# BUSCAR IDS
# ==========================

tempo_df = pd.read_sql(
    "SELECT id_tempo FROM dim_tempo",
    engine
)

paciente_df = pd.read_sql(
    "SELECT id_paciente FROM dim_paciente",
    engine
)

# ==========================
# REGRAS HOSPITAL
# ==========================

ATENDIMENTOS_MES = 6500

setores = {
    1: 0.25,  # Emergência
    2: 0.35,  # PA
    5: 0.10,  # Maternidade
    6: 0.15,  # Cardiologia
    7: 0.08,  # Centro cirúrgico
    3: 0.04,  # UTI Adulto
    4: 0.03   # UTI Neo
}

convenios = {
    1: 0.55,  # SUS
    2: 0.30,  # Unimed
    3: 0.10,  # Bradesco
    4: 0.05   # Particular
}

ticket = {
    1: (100, 500),
    2: (700, 1800),
    3: (900, 2200),
    4: (1200, 3500)
}

dados = []

datas = tempo_df["id_tempo"].tolist()
pacientes = paciente_df["id_paciente"].tolist()

TOTAL = 156000

for _ in range(TOTAL):

    convenio = random.choices(
        list(convenios.keys()),
        weights=convenios.values()
    )[0]

    setor = random.choices(
        list(setores.keys()),
        weights=setores.values()
    )[0]

    tempo_espera = random.randint(5, 180)

    valor = round(
        random.uniform(*ticket[convenio]),
        2
    )

    dados.append({
        "id_tempo":
            random.choice(datas),

        "id_paciente":
            random.choice(pacientes),

        "id_setor":
            setor,

        "id_convenio":
            convenio,

        "tipo_atendimento":
            "Hospitalar",

        "tempo_espera_min":
            tempo_espera,

        "valor_atendimento":
            valor
    })

df = pd.DataFrame(dados)

# backup csv
df.to_csv(
    "data/processed/fato_atendimentos.csv",
    index=False
)

# mysql
df.to_sql(
    "fato_atendimentos",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10000,
    method="multi"
)

print("fato_atendimentos carregada!")
print(df.head())
print(f"Total: {len(df)}")