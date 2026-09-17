import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
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
# GERAR DIM_TEMPO
# ==========================

datas = pd.date_range(
    start="2025-01-01",
    end="2026-12-31"
)

df = pd.DataFrame({
    "data_completa": datas.date,
    "dia": datas.day,
    "mes": datas.month,
    "nome_mes": datas.strftime("%B"),
    "trimestre": datas.quarter,
    "ano": datas.year,
    "dia_semana": datas.strftime("%A"),
    "fim_semana": datas.weekday >= 5
})

# ==========================
# EXPORT CSV (backup)
# ==========================

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

csv_path = output_dir / "dim_tempo.csv"

df.to_csv(csv_path, index=False)

# ==========================
# INSERIR MYSQL
# ==========================

df.to_sql(
    name="dim_tempo",
    con=engine,
    if_exists="append",
    index=False
)

print("dim_tempo carregada com sucesso!")
print(f"Total registros: {len(df)}")