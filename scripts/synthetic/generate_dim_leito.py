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
# LEITOS
# ==========================

estrutura = {
    "Enfermaria": 80,
    "Maternidade": 20,
    "Privativo": 10,
    "UTI Adulto": 10,
    "UTI Neo": 14
}

dados = []

for tipo, qtd in estrutura.items():

    for i in range(1, qtd + 1):

        codigo = f"{tipo[:3].upper()}-{i:03}"

        dados.append({
            "codigo_leito": codigo,
            "tipo_leito": tipo,
            "setor": tipo,
            "ativo": True
        })

df = pd.DataFrame(dados)

# backup
df.to_csv(
    "data/processed/dim_leito.csv",
    index=False
)

# mysql
df.to_sql(
    "dim_leito",
    con=engine,
    if_exists="append",
    index=False
)

print("dim_leito carregada!")
print(df.head())
print(f"Total: {len(df)}")