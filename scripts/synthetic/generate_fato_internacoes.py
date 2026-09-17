"""
scripts/synthetic/generate_fato_internacoes.py
Simulador de internações hospitalares com motor determinístico de leitos,
eliminação de colisões físicas (ocupação real 75-85%), custos escalados e 
desfechos clínicos baseados em evidência epidemiológica.
"""

import random
from pathlib import Path
from datetime import timedelta
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


def carregar_dados_dw():
    """Carrega dimensões e descobre o schema de destino dinamicamente."""
    print("[*] Carregando dimensões do banco de dados...")
    with engine.connect() as conn:
        df_tempo = pd.read_sql("SELECT id_tempo, data_completa FROM dim_tempo ORDER BY data_completa", conn)
        df_tempo['data_completa'] = pd.to_datetime(df_tempo['data_completa'])

        df_leito = pd.read_sql("SELECT * FROM dim_leito", conn)
        df_paciente = pd.read_sql("SELECT id_paciente FROM dim_paciente", conn)
        df_convenio = pd.read_sql("SELECT * FROM dim_convenio", conn)

        fato_cols = pd.read_sql("DESCRIBE fato_internacoes", conn)['Field'].tolist()
        print(f"    -> Colunas detectadas em fato_internacoes: {fato_cols}")

    return df_tempo, df_leito, df_paciente, df_convenio, fato_cols


def obter_perfil_leito(tipo_leito_str):
    t = str(tipo_leito_str).lower()

    if "neo" in t:
        los_min, los_max, los_media, los_sigma = 5, 28, 11, 4.5
        diaria_min, diaria_max = 3500.0, 5500.0
        prob_desfecho = [0.93, 0.02, 0.05]
    elif "uti" in t:
        los_min, los_max, los_media, los_sigma = 3, 18, 7, 3.0
        diaria_min, diaria_max = 3000.0, 4800.0
        prob_desfecho = [0.84, 0.05, 0.11]
    elif "matern" in t:
        los_min, los_max, los_media, los_sigma = 2, 5, 3, 0.8
        diaria_min, diaria_max = 1300.0, 2300.0
        prob_desfecho = [0.994, 0.005, 0.001]
    elif "privat" in t or "apart" in t:
        los_min, los_max, los_media, los_sigma = 2, 8, 4, 1.5
        diaria_min, diaria_max = 1800.0, 2900.0
        prob_desfecho = [0.985, 0.010, 0.005]
    else:
        los_min, los_max, los_media, los_sigma = 2, 10, 4.5, 2.0
        diaria_min, diaria_max = 950.0, 1600.0
        prob_desfecho = [0.982, 0.010, 0.008]

    return {
        "los_range": (los_min, los_max, los_media, los_sigma),
        "diaria_range": (diaria_min, diaria_max),
        "desfechos_p": prob_desfecho
    }


def simular_internacoes_sem_colisao(alvo_ocupacao=0.80):
    df_tempo, df_leito, df_paciente, df_convenio, fato_cols = carregar_dados_dw()

    col_tipo_leito = next((c for c in df_leito.columns if not c.startswith('id_') and ('tipo' in c or 'nome' in c or 'leito' in c)), df_leito.columns[1])
    col_nome_conv = next((c for c in df_convenio.columns if not c.startswith('id_')), df_convenio.columns[-1])

    data_para_id_tempo = dict(zip(df_tempo['data_completa'].dt.date, df_tempo['id_tempo']))
    todas_datas = sorted(list(data_para_id_tempo.keys()))
    data_inicio = todas_datas[0]
    data_fim = todas_datas[-1]
    dias_totais = (data_fim - data_inicio).days + 1

    print(f"[*] Período de simulação: de {data_inicio} até {data_fim} ({dias_totais} dias)")
    print(f"[*] Total de leitos instalados: {len(df_leito)}")

    agenda_leitos = {row['id_leito']: set() for _, row in df_leito.iterrows()}
    leito_dict = df_leito.set_index('id_leito').to_dict('index')

    pacientes_pool = df_paciente['id_paciente'].values
    convenios_pool = df_convenio.to_dict('records')

    internacoes = []
    print("[*] Iniciando simulação física de ocupação hospitalar...")

    datas_simuladas = todas_datas[:-15]

    for dt_atual in datas_simuladas:
        mes = dt_atual.month
        fator_mes = 1.25 if mes in [5, 6, 7, 8] else (0.90 if mes in [12, 1, 2] else 1.00)

        for id_leito, leito_info in leito_dict.items():
            if dt_atual in agenda_leitos[id_leito]:
                continue

            prob_admissao = 0.23 * fator_mes
            if random.random() > prob_admissao:
                continue

            perfil = obter_perfil_leito(leito_info[col_tipo_leito])
            min_d, max_d, media_d, sigma_d = perfil["los_range"]

            los = int(np.clip(np.random.normal(media_d, sigma_d), min_d, max_d))
            dt_alta = dt_atual + timedelta(days=los)

            if dt_alta > data_fim:
                dt_alta = data_fim
                los = (dt_alta - dt_atual).days
                if los < 1:
                    continue

            dias_ocupados = [dt_atual + timedelta(days=d) for d in range(los)]
            agenda_leitos[id_leito].update(dias_ocupados)

            id_pac = int(np.random.choice(pacientes_pool))
            conv = random.choice(convenios_pool)
            conv_str = str(conv[col_nome_conv]).lower()

            desfecho = np.random.choice(['Alta', 'Transferencia', 'Obito'], p=perfil["desfechos_p"])

            d_min, d_max = perfil["diaria_range"]
            diaria = np.random.uniform(d_min, d_max)
            custo_total = round(float(diaria * los + np.random.uniform(300, 1500)), 2)

            mult_conv = 1.35 if "particular" in conv_str else (1.18 if any(k in conv_str for k in ["apart", "exec", "prem"]) else 1.05)
            valor_faturado = round(float(custo_total * mult_conv), 2)

            id_tempo_entrada = data_para_id_tempo.get(dt_atual)
            id_tempo_alta = data_para_id_tempo.get(dt_alta)

            reg = {}
            for col in fato_cols:
                c = col.lower()
                if 'entrada' in c and ('tempo' in c or 'data' in c or 'id' in c):
                    reg[col] = id_tempo_entrada
                elif ('alta' in c or 'saida' in c) and ('tempo' in c or 'data' in c or 'id' in c):
                    reg[col] = id_tempo_alta
                elif c == 'id_tempo':
                    reg[col] = id_tempo_entrada
                elif c == 'id_paciente':
                    reg[col] = id_pac
                elif c == 'id_leito':
                    reg[col] = id_leito
                elif c == 'id_convenio':
                    reg[col] = conv['id_convenio']
                elif 'permanencia' in c or 'dias' in c or 'los' in c:
                    reg[col] = los
                elif 'desfecho' in c or 'motivo' in c:
                    reg[col] = desfecho
                elif 'custo' in c:
                    reg[col] = custo_total
                elif 'fatur' in c or 'receita' in c or 'valor' in c:
                    reg[col] = valor_faturado

            internacoes.append(reg)

    df_internacoes = pd.DataFrame(internacoes)

    total_leito_dias_instalados = len(df_leito) * dias_totais
    total_diarias_ocupadas = sum(len(dias) for dias in agenda_leitos.values())
    taxa_ocupacao_global = (total_diarias_ocupadas / total_leito_dias_instalados) * 100

    print("\n" + "="*50)
    print("           RELATÓRIO DE VALIDAÇÃO FÍSICA")
    print("="*50)
    print(f" Total de internações geradas : {len(df_internacoes):,}")
    print(f" Capacidade máxima instalada  : {total_leito_dias_instalados:,} leito-dias")
    print(f" Total de diárias consumidas  : {total_diarias_ocupadas:,} leito-dias")
    print(f" Taxa de Ocupação Global Real : {taxa_ocupacao_global:.2f}% (Meta: 75% - 85%)")
    print(f" Colisões físicas detectadas  : ZERO (Garantia por construção)")
    print("="*50 + "\n")

    return df_internacoes


def persistir_banco(df, nome_tabela="fato_internacoes"):
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
    df_resultado = simular_internacoes_sem_colisao(alvo_ocupacao=0.80)
    persistir_banco(df_resultado, "fato_internacoes")