"""
scripts/main.py
Orquestrador Principal do Pipeline de Dados da Plataforma Hospitalar.

Fluxo de Execução:
1. Executa a geração e carga das Dimensões (Tempo -> Paciente -> Leito).
2. Executa a geração e carga dos Fatos (Atendimentos -> Internações).
3. Lê e aplica automaticamente as Views Analíticas (sql/views/*.sql) no MySQL.
"""

import sys
import time
from pathlib import Path
import runpy
from sqlalchemy import text

# 1. Configuração de caminhos absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
SYNTHETIC_DIR = SCRIPTS_DIR / "synthetic"
VIEWS_DIR = ROOT_DIR / "sql" / "views"

# Garante a raiz e a pasta synthetic no PYTHONPATH para resolver 'from db import engine'
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SYNTHETIC_DIR))

# Importa a engine central configurada em scripts/synthetic/db.py
from db import engine

# 2. Definição do Pipeline sequencial (Dimensões -> Fatos)
PIPELINE = [
    ("Dimensão Tempo", SYNTHETIC_DIR / "generate_dim_tempo.py"),
    ("Dimensão Paciente", SYNTHETIC_DIR / "generate_dim_paciente.py"),
    ("Dimensão Leito", SYNTHETIC_DIR / "generate_dim_leito.py"),
    ("Fato Atendimentos", SYNTHETIC_DIR / "generate_fato_atendimentos.py"),
    ("Fato Internações", SYNTHETIC_DIR / "generate_fato_internacoes.py"),
]


def apply_views():
    """
    Localiza todos os arquivos .sql em sql/views/ e executa no MySQL
    para garantir que os dashboards do Metabase encontrem os dados agregados.
    """
    print("\n" + "-" * 60)
    print("📊 [Etapa Final] Aplicando Views Analíticas no MySQL...")
    print("-" * 60)

    if not VIEWS_DIR.exists():
        print(f"⚠️ Diretório de views não encontrado: {VIEWS_DIR}")
        return

    view_files = sorted(VIEWS_DIR.glob("*.sql"))

    if not view_files:
        print("⚠️ Nenhum arquivo .sql encontrado em sql/views/.")
        return

    with engine.connect() as connection:
        for view_path in view_files:
            print(f"[*] Criando/atualizando view: {view_path.name}...")
            with open(view_path, "r", encoding="utf-8") as f:
                sql_content = f.read().strip()

            if sql_content:
                connection.execute(text(sql_content))
                connection.commit()
                print(f"[✓] {view_path.name} aplicada com sucesso!")

    print("\n[✓] Todas as views analíticas foram consolidadas no banco de dados!")


def main():
    total_start = time.time()
    print("=" * 60)
    print("🏥 HOSPITAL ANALYTICS PLATFORM - PIPELINE ETL & DW")
    print("=" * 60)

    # Execução das Dimensões e Fatos
    for step_num, (step_name, script_path) in enumerate(PIPELINE, start=1):
        if not script_path.exists():
            print(f"\n❌ [ERRO CRÍTICO] Script não encontrado: {script_path.name}")
            sys.exit(1)

        print(f"\n[{step_num}/{len(PIPELINE)}] Executando {step_name} ({script_path.name})...")
        step_start = time.time()

        try:
            # Executa o script isoladamente como se fosse chamado via terminal
            runpy.run_path(str(script_path), run_name="__main__")
            elapsed = time.time() - step_start
            print(f"[✓] {step_name} finalizado em {elapsed:.1f}s.")
        except Exception as e:
            print(f"\n❌ [FALHA] Erro durante a execução de {step_name}: {e}")
            sys.exit(1)

    # Execução da criação das views analíticas
    try:
        apply_views()
    except Exception as e:
        print(f"\n❌ [FALHA] Erro ao aplicar views analíticas: {e}")
        sys.exit(1)

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"🎉 Pipeline concluído com sucesso em {total_elapsed:.1f} segundos!")
    print("Os dados e views estão prontos para consumo no Metabase.")
    print("=" * 60)


if __name__ == "__main__":
    main()