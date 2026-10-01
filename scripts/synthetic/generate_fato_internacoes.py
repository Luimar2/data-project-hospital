"""
scripts/synthetic/generate_fato_internacoes.py
Simulador de internações hospitalares com motor determinístico de leitos,
eliminação de colisões físicas, desfechos epidemiologicamente calibrados e 
continuidade temporal até o último dia do período.
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
        # UTI Neo: permanência mais longa, baixa mortalidade neonatal intermediária
        los_min, los_max, los_media, los_sigma = 6, 28, 12, 4.0
        diaria_min, diaria_max = 3500.0, 5400.0
        prob_desfecho = [0.945, 0.030, 0.025]  # ~2.5% óbito
    elif "uti" in t:
        # UTI Adulto: casos críticos, maior concentração de óbitos hospitalares
        los_min, los_max, los_media, los_sigma = 3, 20, 7, 3.2
        diaria_min, diaria_max = 3100.0, 4900.0
        prob_desfecho = [0.770, 0.060, 0.170]  # ~17% óbito
    elif "matern" in t:
        # Maternidade: permanência curta, óbito materno sentinela (zerado)
        los_min, los_max, los_media, los_sigma = 2, 4, 2.5, 0.6
        diaria_min, diaria_max = 1300.0, 2200.0
        prob_desfecho = [0.997, 0.003, 0.000]  # 0% óbito
    elif "privat" in t or "apart" in t:
        # Privativo: cirurgias eletivas e internações clínicas de convênio/particular
        los_min, los_max, los_media, los_sigma = 2, 8, 3.8, 1.4
        diaria_min, diaria_max = 1900.0, 3100.0
        prob_desfecho = [0.985, 0.010, 0.005]  # 0.5% óbito
    else:
        # Enfermaria: internações clínicas e cirúrgicas gerais
        los_min, los_max, los_media, los_sigma = 2, 10, 4.6, 1.8
        diaria_min, diaria_max = 980.0, 1650.0
        prob_desfecho = [0.970, 0.018, 0.012]  # 1.2% óbito

    return {
        "los_range": (los_min, los_max, los_media, los_sigma),
        "diaria_range": (diaria_min, diaria_max),
        "desfechos_p": prob_desfecho
    }


def selecionar_convenio_por_leito(tipo_leito_str, convenios, col_nome_conv):
    t = str(tipo_leito_str).lower()
    pesos = []

    for c in convenios:
        nome_c = str(c[col_nome_conv]).lower()
        if "privat" in t:
            if "particular" in nome_c:
                pesos.append(0.35)
            elif "sus" in nome_c:
                pesos.append(0.05)
            else:
                pesos.append(0.30)
        elif "enferm" in t:
            if "sus" in nome_c:
                pesos.append(0.55)
            elif "particular" in nome_c:
                pesos.append(0.05)
            else:
                pesos.append(0.20)
        else:  # UTI, Maternidade
            if "sus" in nome_c:
                pesos.append(0.40)
            elif "particular" in nome_c:
                pesos.append(0.12)
            else:
                pesos.append(0.24)

    prob = np.array(pesos) / sum(pesos)
    idx = np.random.choice(len(convenios), p=prob)
    return convenios[idx]


def simular_internacoes_sem_colisao(alvo_ocupacao=0.80):
    df_tempo, df_leito, df_paciente, df_convenio, fato_cols = carregar_dados_dw()

    col_tipo_leito = next(
        (c for c in df_leito.columns if not c.startswith('id_') and ('tipo' in c or 'nome' in c or 'leito' in c)),
        df_leito.columns[1]
    )
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
    print("[*] Simulando ocupação física contínua até o último dia...")

    # Sem o corte de [:-15] para evitar despencar no fim do ano
    for dt_atual in todas_datas:
        mes = dt_atual.month
        fator_mes = 1.22 if mes in [5, 6, 7, 8] else (0.92 if mes in [12, 1, 2] else 1.00)

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

            # Ajuste de limite do período sem truncar artificialmente
            if dt_alta > data_fim:
                dt_alta = data_fim
                los = max(1, (dt_alta - dt_atual).days)

            dias_ocupados = [dt_atual + timedelta(days=d) for d in range(los)]
            agenda_leitos[id_leito].update(dias_ocupados)

            id_pac = int(np.random.choice(pacientes_pool))
            conv = selecionar_convenio_por_leito(leito_info[col_tipo_leito], convenios_pool, col_nome_conv)
            conv_str = str(conv[col_nome_conv]).lower()

            desfecho = np.random.choice(['Alta', 'Transferência', 'Óbito'], p=perfil["desfechos_p"])

            d_min, d_max = perfil["diaria_range"]
            diaria = np.random.uniform(d_min, d_max)
            custo_total = round(float(diaria * los + np.random.uniform(250, 1400)), 2)

            mult_conv = (
                np.random.uniform(1.30, 1.45) if "particular" in conv_str
                else (np.random.uniform(1.15, 1.25) if any(k in conv_str for k in ["apart", "exec", "prem", "bradesco"])
                else np.random.uniform(1.03, 1.10))
            )
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
    df_resultado = simular_internacoes_sem_colisao(alvo_ocupacao=0.80)
    persistir_banco(df_resultado, "fato_internacoes")