"""
generate_fato_atendimentos.py
Geração sintética de atendimentos ambulatoriais e de urgência
com plausibilidade clínica, sazonalidade e introspecção dinâmica de schema.
"""

import os
import random
from urllib.parse import quote_plus
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# 1. Reprodutibilidade
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# 2. Conexão MySQL (.env)
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


def carregar_dimensoes():
    """Carrega as dimensões inspecionando dinamicamente as colunas existentes."""
    print("[*] Carregando dimensões do banco de dados...")
    with engine.connect() as conn:
        # 1. dim_tempo (usa 'data_completa' confirmada)
        df_tempo = pd.read_sql("SELECT id_tempo, data_completa, mes FROM dim_tempo", conn)
        df_tempo.rename(columns={'data_completa': 'data'}, inplace=True)
        df_tempo['data'] = pd.to_datetime(df_tempo['data'])

        # 2. dim_paciente
        df_paciente = pd.read_sql("SELECT id_paciente FROM dim_paciente", conn)

        # 3. dim_setor
        df_setor = pd.read_sql("SELECT * FROM dim_setor", conn)

        # 4. dim_convenio
        df_convenio = pd.read_sql("SELECT * FROM dim_convenio", conn)

        # 5. Inspeciona colunas reais da fato_atendimentos
        fato_cols = pd.read_sql("DESCRIBE fato_atendimentos", conn)['Field'].tolist()
        print(f"    -> Colunas detectadas em fato_atendimentos: {fato_cols}")

    return df_tempo, df_paciente, df_setor, df_convenio, fato_cols


def calcular_pesos_temporais(df_tempo):
    pesos_mes = {
        1: 0.90, 2: 0.92, 3: 1.00, 4: 1.05,
        5: 1.20, 6: 1.25, 7: 1.25, 8: 1.15,
        9: 1.00, 10: 1.02, 11: 0.98, 12: 0.92
    }
    df_tempo_calc = df_tempo.copy()
    df_tempo_calc['peso_mes'] = df_tempo_calc['mes'].map(pesos_mes).fillna(1.0)
    df_tempo_calc['is_weekend'] = df_tempo_calc['data'].dt.dayofweek.isin([5, 6])
    return df_tempo_calc


def amostrar_tempo_espera(nome_setor):
    setor_lower = str(nome_setor).lower()
    if "emerg" in setor_lower:
        val = np.random.lognormal(mean=2.89, sigma=0.45)  # Mediana ~18 min
    elif "pronto" in setor_lower:
        val = np.random.lognormal(mean=4.17, sigma=0.55)  # Mediana ~65 min
    elif "cirurg" in setor_lower:
        val = np.random.lognormal(mean=3.55, sigma=0.30)  # ~35 min
    else:
        val = np.random.lognormal(mean=3.80, sigma=0.40)  # ~45 min
    return int(np.clip(val, 5, 240))


def definir_tipo_e_valores(nome_setor, info_convenio_str):
    setor_lower = str(nome_setor).lower()

    if "emerg" in setor_lower or "pronto" in setor_lower:
        tipos = ['Urgência / Emergência', 'Consulta Ambulatorial', 'Exame / Procedimento']
        probs = [0.75, 0.15, 0.10]
    elif "cirurg" in setor_lower:
        tipos = ['Pequena Cirurgia', 'Exame / Procedimento']
        probs = [0.80, 0.20]
    else:
        tipos = ['Consulta Ambulatorial', 'Exame / Procedimento', 'Pequena Cirurgia']
        probs = [0.65, 0.30, 0.05]

    tipo_atendimento = np.random.choice(tipos, p=probs)

    if tipo_atendimento == 'Pequena Cirurgia':
        tempo_atendimento = int(np.clip(np.random.normal(75, 20), 30, 180))
        custo_base = np.random.uniform(850.0, 2400.0)
    elif tipo_atendimento == 'Exame / Procedimento':
        tempo_atendimento = int(np.clip(np.random.normal(30, 10), 10, 90))
        custo_base = np.random.uniform(150.0, 600.0)
    elif tipo_atendimento == 'Urgência / Emergência':
        tempo_atendimento = int(np.clip(np.random.normal(45, 15), 15, 120))
        custo_base = np.random.uniform(280.0, 950.0)
    else:
        tempo_atendimento = int(np.clip(np.random.normal(25, 8), 10, 60))
        custo_base = np.random.uniform(120.0, 350.0)

    # Multiplicador se particular ou premium
    mult_convenio = 1.0
    conv_lower = str(info_convenio_str).lower()
    if "particular" in conv_lower:
        mult_convenio = 1.35
    elif any(k in conv_lower for k in ["apartamento", "executivo", "premium", "especial"]):
        mult_convenio = 1.15

    custo_total = round(float(custo_base), 2)
    valor_faturado = round(float(custo_base * mult_convenio), 2)

    return tipo_atendimento, tempo_atendimento, custo_total, valor_faturado


def gerar_fato_atendimentos(num_registros=50000):
    df_tempo, df_paciente, df_setor, df_convenio, fato_cols = carregar_dimensoes()
    df_tempo_calc = calcular_pesos_temporais(df_tempo)

    # IDENTIFICAÇÃO CORRETA: ignora colunas 'id_'
    col_nome_setor = next((c for c in df_setor.columns if not c.startswith('id_') and ('nome' in c or 'setor' in c or 'desc' in c)), 'nome_setor')
    col_nome_conv = next((c for c in df_convenio.columns if not c.startswith('id_')), df_convenio.columns[-1])

    print(f"[*] Coluna textual detectada para setor: '{col_nome_setor}'")
    print(f"[*] Coluna textual detectada para convênio: '{col_nome_conv}'")
    print(f"[*] Setores encontrados: {df_setor[col_nome_setor].tolist()}")
    print(f"[*] Gerando {num_registros:,} atendimentos com diferenciação clínica real...")

    paciente_ids = df_paciente['id_paciente'].values
    setores = df_setor.to_dict('records')
    convenios = df_convenio.to_dict('records')

    pesos_urgencia = (df_tempo_calc['peso_mes'] * np.where(df_tempo_calc['is_weekend'], 1.08, 1.00)).values
    prob_urgencia = pesos_urgencia / pesos_urgencia.sum()

    pesos_eletivo = (df_tempo_calc['peso_mes'] * np.where(df_tempo_calc['is_weekend'], 0.20, 1.00)).values
    prob_eletivo = pesos_eletivo / pesos_eletivo.sum()

    datas_indices = np.arange(len(df_tempo_calc))
    registros = []

    for i in range(num_registros):
        setor = random.choice(setores)
        nome_setor = str(setor[col_nome_setor])

        is_urgencia = any(k in nome_setor.lower() for k in ['emerg', 'pronto'])
        data_idx = np.random.choice(datas_indices, p=(prob_urgencia if is_urgencia else prob_eletivo))
        id_tempo = int(df_tempo_calc.iloc[data_idx]['id_tempo'])

        id_paciente = int(np.random.choice(paciente_ids))
        convenio = random.choice(convenios)

        tempo_espera = amostrar_tempo_espera(nome_setor)
        tipo_atend, tempo_atend, custo, faturado = definir_tipo_e_valores(nome_setor, convenio[col_nome_conv])

        reg = {}
        for col in fato_cols:
            c = col.lower()
            if c == 'id_tempo':
                reg[col] = id_tempo
            elif c == 'id_paciente':
                reg[col] = id_paciente
            elif c == 'id_setor':
                reg[col] = setor['id_setor']
            elif c == 'id_convenio':
                reg[col] = convenio['id_convenio']
            elif 'tipo' in c:
                reg[col] = tipo_atend
            elif 'espera' in c:
                reg[col] = tempo_espera
            elif 'atendimento' in c and ('tempo' in c or 'min' in c):
                reg[col] = tempo_atend
            elif 'custo' in c:
                reg[col] = custo
            elif 'fatur' in c or 'receita' in c or 'valor' in c:
                reg[col] = faturado

        registros.append(reg)

        if (i + 1) % 10000 == 0:
            print(f"    -> {i + 1:,} registros processados...")

    df_fato = pd.DataFrame(registros)
    return df_fato


def persistir_banco(df_fato):
    print(f"[*] Inserindo {len(df_fato):,} registros na tabela fato_atendimentos...")
    df_fato.to_sql(
        name="fato_atendimentos",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print("[✓] Carga de fato_atendimentos finalizada com sucesso!")


if __name__ == "__main__":
    df_resultado = gerar_fato_atendimentos(num_registros=50000)
    persistir_banco(df_resultado)