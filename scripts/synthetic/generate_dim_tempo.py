"""
scripts/synthetic/generate_dim_tempo.py
Geração da dimensão de tempo com granularidade diária.
"""

from pathlib import Path
import pandas as pd
from db import engine

# Configuração de diretório de backup na raiz
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gerar_dim_tempo(start_date="2025-01-01", end_date="2026-12-31"):
    print(f"[*] Gerando dim_tempo de {start_date} até {end_date}...")
    datas = pd.date_range(start=start_date, end=end_date)

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

    return df


def persistir_banco(df, nome_tabela="dim_tempo"):
    # 1. Salva Backup CSV
    csv_path = OUTPUT_DIR / f"{nome_tabela}.csv"
    print(f"[*] Salvando backup em: {csv_path}...")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[✓] Backup CSV concluído com sucesso!")

    # 2. Inserção otimizada no MySQL
    print(f"[*] Inserindo {len(df):,} registros na tabela {nome_tabela}...")
    df.to_sql(
        name=nome_tabela,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print(f"[✓] Carga de {nome_tabela} finalizada com sucesso!")


if __name__ == "__main__":
    df_tempo = gerar_dim_tempo(start_date="2025-01-01", end_date="2026-12-31")
    persistir_banco(df_tempo, "dim_tempo")