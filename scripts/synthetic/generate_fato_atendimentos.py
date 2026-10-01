"""
scripts/synthetic/generate_fato_atendimentos.py
Geração sintética de atendimentos ambulatoriais e de urgência
com plausibilidade clínica, sazonalidade e fluxo estocástico não-arredondado.
"""

import random
from pathlib import Path
import numpy as np
import pandas as pd
from db import engine

# 1. Reprodutibilidade
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# 2. Diretório de backup na raiz
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def carregar_dimensoes():
    print("[*] Carregando dimensões do banco de dados...")
    with engine.connect() as conn:
        df_tempo = pd.read_sql("SELECT id_tempo, data_completa, mes, dia_semana FROM dim_tempo ORDER BY data_completa", conn)
        df_tempo.rename(columns={'data_completa': 'data'}, inplace=True)
        df_tempo['data'] = pd.to_datetime(df_tempo['data'])

        df_paciente = pd.read_sql("SELECT id_paciente FROM dim_paciente", conn)
        df_setor = pd.read_sql("SELECT * FROM dim_setor", conn)
        df_convenio = pd.read_sql("SELECT * FROM dim_convenio", conn)

        fato_cols = pd.read_sql("DESCRIBE fato_atendimentos", conn)['Field'].tolist()
        print(f"    -> Colunas detectadas em fato_atendimentos: {fato_cols}")

    return df_tempo, df_paciente, df_setor, df_convenio, fato_cols


def filtrar_setores_porta_entrada(df_setor):
    col_nome_setor = next(
        (c for c in df_setor.columns if not c.startswith('id_') and ('nome' in c or 'setor' in c or 'desc' in c)),
        'nome_setor'
    )
    # Apenas setores de porta de entrada / ambulatoriais
    setores_validos = []
    pesos_setores = []

    for _, row in df_setor.iterrows():
        nome = str(row[col_nome_setor]).lower()
        if "pronto" in nome:
            setores_validos.append(row.to_dict())
            pesos_setores.append(0.60)
        elif "emerg" in nome:
            setores_validos.append(row.to_dict())
            pesos_setores.append(0.28)
        elif "cardio" in nome or "ambulat" in nome or "consult" in nome:
            setores_validos.append(row.to_dict())
            pesos_setores.append(0.12)

    # Fallback se não encontrar os nomes específicos
    if not setores_validos:
        print("[!] Atenção: Setores de porta não encontrados nominalmente. Usando setores não-críticos.")
        for _, row in df_setor.iterrows():
            nome = str(row[col_nome_setor]).lower()
            if not any(k in nome for k in ["uti", "cirurg"]):
                setores_validos.append(row.to_dict())
                pesos_setores.append(1.0)
        pesos_setores = [p / sum(pesos_setores) for p in pesos_setores]
    else:
        pesos_setores = [p / sum(pesos_setores) for p in pesos_setores]

    return setores_validos, pesos_setores, col_nome_setor


def amostrar_convenio_por_setor(nome_setor, convenios, col_nome_conv):
    setor_lower = str(nome_setor).lower()
    pesos = []
    for conv in convenios:
        nome_c = str(conv[col_nome_conv]).lower()
        if "emerg" in setor_lower or "pronto" in setor_lower:
            if "sus" in nome_c:
                pesos.append(0.48)
            elif "partic" in nome_c:
                pesos.append(0.08)
            else:  # Bradesco, Unimed, etc.
                pesos.append(0.22)
        else:  # Ambulatório / Consultórios
            if "sus" in nome_c:
                pesos.append(0.20)
            elif "partic" in nome_c:
                pesos.append(0.20)
            else:
                pesos.append(0.30)

    prob = np.array(pesos) / sum(pesos)
    idx = np.random.choice(len(convenios), p=prob)
    return convenios[idx]


def amostrar_tempo_espera(nome_setor):
    setor_lower = str(nome_setor).lower()
    if "emerg" in setor_lower:
        # Emergência: triagem rápida
        val = np.random.lognormal(mean=2.85, sigma=0.40)  # ~17 a 25 min
    elif "pronto" in setor_lower:
        # PA: maior volume, filas nos picos
        val = np.random.lognormal(mean=4.15, sigma=0.45)  # ~55 a 85 min
    else:
        # Consultório / Ambulatório agendado
        val = np.random.lognormal(mean=3.20, sigma=0.35)  # ~22 a 32 min
    return int(np.clip(val, 5, 240))


def definir_tipo_e_valores(nome_setor, info_convenio_str):
    setor_lower = str(nome_setor).lower()

    if "emerg" in setor_lower:
        tipos = ['Urgência / Emergência', 'Exame / Procedimento']
        probs = [0.85, 0.15]
    elif "pronto" in setor_lower:
        tipos = ['Urgência / Emergência', 'Consulta Ambulatorial', 'Exame / Procedimento']
        probs = [0.70, 0.20, 0.10]
    else:
        tipos = ['Consulta Ambulatorial', 'Exame / Procedimento']
        probs = [0.80, 0.20]

    tipo_atendimento = np.random.choice(tipos, p=probs)

    # Ruído estocástico no custo base
    if tipo_atendimento == 'Urgência / Emergência':
        tempo_atendimento = int(np.clip(np.random.normal(45, 12), 15, 120))
        custo_base = np.random.uniform(280.0, 920.0) * np.random.uniform(0.92, 1.08)
    elif tipo_atendimento == 'Exame / Procedimento':
        tempo_atendimento = int(np.clip(np.random.normal(30, 8), 10, 80))
        custo_base = np.random.uniform(140.0, 580.0) * np.random.uniform(0.92, 1.08)
    else:
        tempo_atendimento = int(np.clip(np.random.normal(25, 6), 10, 50))
        custo_base = np.random.uniform(130.0, 320.0) * np.random.uniform(0.92, 1.08)

    # Multiplicador realista de faturamento por convênio
    conv_lower = str(info_convenio_str).lower()
    if "particular" in conv_lower:
        mult_convenio = np.random.uniform(1.30, 1.48)
    elif "sus" in conv_lower:
        mult_convenio = np.random.uniform(1.02, 1.08)
    elif "bradesco" in conv_lower:
        mult_convenio = np.random.uniform(1.18, 1.28)
    else:  # Unimed / outros
        mult_convenio = np.random.uniform(1.14, 1.24)

    custo_total = round(float(custo_base), 2)
    valor_faturado = round(float(custo_base * mult_convenio), 2)

    return tipo_atendimento, tempo_atendimento, custo_total, valor_faturado


def gerar_fato_atendimentos():
    df_tempo, df_paciente, df_setor, df_convenio, fato_cols = carregar_dimensoes()
    setores_validos, pesos_setores, col_nome_setor = filtrar_setores_porta_entrada(df_setor)

    col_nome_conv = next((c for c in df_convenio.columns if not c.startswith('id_')), df_convenio.columns[-1])
    convenios = df_convenio.to_dict('records')
    paciente_ids = df_paciente['id_paciente'].values

    pesos_mes = {
        1: 0.90, 2: 0.92, 3: 1.00, 4: 1.05,
        5: 1.20, 6: 1.25, 7: 1.22, 8: 1.15,
        9: 1.00, 10: 1.02, 11: 0.98, 12: 0.92
    }

    print("[*] Gerando fluxo diário estocástico de atendimentos (biênio 2025-2026)...")
    registros = []

    # Simulação dia a dia para quebrar número redondo
    for _, dia_row in df_tempo.iterrows():
        id_tempo = int(dia_row['id_tempo'])
        mes = dia_row['mes']
        is_fim_semana = dia_row['data'].dayofweek in [5, 6]

        fator_sazonal = pesos_mes.get(mes, 1.0)
        base_dia = 68.0 if is_fim_semana else 74.0

        # Quantidade orgânica de atendimentos no dia (Poisson com ruído)
        lambda_dia = base_dia * fator_sazonal
        qtd_atendimentos_dia = np.random.poisson(lam=lambda_dia)

        for _ in range(qtd_atendimentos_dia):
            setor = np.random.choice(setores_validos, p=pesos_setores)
            nome_setor = str(setor[col_nome_setor])

            id_paciente = int(np.random.choice(paciente_ids))
            convenio = amostrar_convenio_por_setor(nome_setor, convenios, col_nome_conv)

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

    df_resultado = pd.DataFrame(registros)
    print(f"[✓] Concluído! Total orgânico gerado: {len(df_resultado):,} atendimentos no biênio.")
    return df_resultado


def persistir_banco(df, nome_tabela="fato_atendimentos"):
    csv_path = OUTPUT_DIR / f"{nome_tabela}.csv"
    print(f"[*] Salvando backup em: {csv_path}...")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[✓] Backup CSV concluído com sucesso!")

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
    df_fato = gerar_fato_atendimentos()
    persistir_banco(df_fato, "fato_atendimentos")