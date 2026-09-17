import os
import random
from urllib.parse import quote_plus
from dotenv import load_dotenv
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine

# ==========================
# CONFIGURAÇÃO MYSQL (.env)
# ==========================

load_dotenv()

DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_NAME = os.getenv("MYSQL_DATABASE")

password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# ==========================
# CONFIG
# ==========================

fake = Faker("pt_BR")
TOTAL_PACIENTES = 10000

cidades = [
    "Florianópolis",
    "São José",
    "Palhoça",
    "Biguaçu",
    "Itajaí",
    "Balneário Camboriú",
    "Tijucas"
]

sexo_lista = ["Masculino", "Feminino"]

dados = []

for _ in range(TOTAL_PACIENTES):

    idade = random.randint(0, 95)

    if idade <= 12:
        faixa = "Infantil"
    elif idade <= 17:
        faixa = "Adolescente"
    elif idade <= 59:
        faixa = "Adulto"
    else:
        faixa = "Idoso"

    dados.append({
        "sexo": random.choice(sexo_lista),
        "faixa_etaria": faixa,
        "cidade": random.choice(cidades),
        "idade": idade
    })

df = pd.DataFrame(dados)

# salva csv backup
df.to_csv(
    "data/processed/dim_paciente.csv",
    index=False
)

# mysql
df.to_sql(
    "dim_paciente",
    con=engine,
    if_exists="append",
    index=False
)

print("dim_paciente carregada!")
print(df.head())
print(f"Total: {len(df)}")