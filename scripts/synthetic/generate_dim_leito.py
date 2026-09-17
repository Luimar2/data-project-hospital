"""
scripts/synthetic/generate_dim_leito.py
Geração da dimensão de leitos hospitalares categorizados por tipo e setor.
"""

from pathlib import Path
import pandas as pd
from db import engine

# Configuração de diretório de backup na raiz
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gerar_dim_leito():
    print("[*] Gerando estrutura de leitos do hospital...")
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

    return pd.DataFrame(dados)


def persistir_banco(df, nome_tabela="dim_leito"):
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
    df_leito = gerar_dim_leito()
    persistir_banco(df_leito, "dim_leito")