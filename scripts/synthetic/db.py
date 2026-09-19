"""
scripts/synthetic/db.py
Módulo central de conexão para a geração de dados sintéticos.
Localiza o .env na raiz do projeto, valida credenciais e força utf8mb4.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Caminho: synthetic/ -> scripts/ -> raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

# 1. Valida existência física do .env
if not ENV_PATH.exists():
    raise FileNotFoundError(
        f"\n[ERRO CRÍTICO] Arquivo .env não encontrado na raiz!\n"
        f"Caminho esperado: {ENV_PATH}"
    )

load_dotenv(dotenv_path=ENV_PATH)

# 2. Valida variáveis obrigatórias
REQUIRED_VARS = [
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_DATABASE"
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(
        f"\n[ERRO CRÍTICO] Variáveis ausentes no .env: {', '.join(missing)}"
    )

# 3. Credenciais e URL com charset utf8mb4 explícito
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_NAME = os.getenv("MYSQL_DATABASE")

password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# 4. Engine com garantia de UTF-8 e pool resiliente
engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4"},
    pool_pre_ping=True
)