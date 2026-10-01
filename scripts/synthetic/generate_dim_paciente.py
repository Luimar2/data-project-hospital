"""
scripts/synthetic/generate_dim_paciente.py
"""
import random
from pathlib import Path
from faker import Faker
import pandas as pd
from db import engine

fake = Faker("pt_BR")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gerar_dim_paciente(total_pacientes=10000):
    print(f"[*] Gerando {total_pacientes:,} pacientes sintéticos...")
    cidades = [
        "Florianópolis", "São José", "Palhoça", 
        "Biguaçu", "Itajaí", "Balneário Camboriú", "Tijucas"
    ]
    sexo_lista = ["Masculino", "Feminino"]
    dados = []

    for _ in range(total_pacientes):
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

    return pd.DataFrame(dados)


def persistir_banco(df, nome_tabela):
    # 1. Salva Backup CSV
    csv_path = OUTPUT_DIR / f"{nome_tabela}.csv"
    print(f"[*] Salvando backup em: {csv_path}...")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[✓] Backup CSV concluído!")

    # 2. Insere no MySQL em lote otimizado
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
    df_paciente = gerar_dim_paciente(total_pacientes=10000)
    persistir_banco(df_paciente, "dim_paciente")