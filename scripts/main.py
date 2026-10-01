"""
scripts/main.py
Orquestrador Principal do Pipeline de Dados da Plataforma Hospitalar.

Fluxo de Execução Idempotente:
1. Healthcheck do MySQL.
2. Limpeza limpa de tabelas e views legadas (Drop prévio seguro).
3. Aplicação dos Schemas DDL (sql/schemas/*.sql).
4. Aplicação dos Seeds estáticos (sql/seeds/*.sql).
5. Geração e carga dos dados sintéticos (Dimensões -> Fatos).
6. Compilação das Views Analíticas (sql/views/*.sql).
"""

import sys
import time
from pathlib import Path
import runpy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# 1. Configuração de caminhos absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
SYNTHETIC_DIR = SCRIPTS_DIR / "synthetic"
SCHEMAS_DIR = ROOT_DIR / "sql" / "schemas"
SEEDS_DIR = ROOT_DIR / "sql" / "seeds"
VIEWS_DIR = ROOT_DIR / "sql" / "views"

# Garante visibilidade dos módulos internos
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SYNTHETIC_DIR))

from db import engine

# 2. Definição do Pipeline sequencial de dados sintéticos
PIPELINE = [
    ("Dimensão Tempo", SYNTHETIC_DIR / "generate_dim_tempo.py"),
    ("Dimensão Paciente", SYNTHETIC_DIR / "generate_dim_paciente.py"),
    ("Dimensão Leito", SYNTHETIC_DIR / "generate_dim_leito.py"),
    ("Fato Atendimentos", SYNTHETIC_DIR / "generate_fato_atendimentos.py"),
    ("Fato Internações", SYNTHETIC_DIR / "generate_fato_internacoes.py"),
]


def wait_for_mysql(max_retries=20, delay=3):
    """Aguarda o container do MySQL estar 100% pronto para aceitar conexões."""
    print("⏳ [1/6] Verificando conexão com o banco de dados MySQL...")
    retries = 0
    while retries < max_retries:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Conexão com o MySQL estabelecida com sucesso!")
            return True
        except OperationalError:
            retries += 1
            print(f"[*] MySQL inicializando... Tentativa {retries}/{max_retries}. Aguardando {delay}s...")
            time.sleep(delay)
        except Exception as e:
            print(f"❌ Erro inesperado ao conectar ao banco: {e}")
            sys.exit(1)

    print("❌ [ERRO] Tempo limite esgotado esperando pelo MySQL.")
    print("   Verifique se o container está ativo: docker compose -f docs/docker-compose.yml ps")
    sys.exit(1)


def execute_sql_file(connection, file_path: Path):
    """Lê um arquivo SQL e executa instrução por instrução de forma segura."""
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read().strip()

    if not sql_content:
        return

    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    for stmt in statements:
        connection.execute(text(stmt))


def reset_database():
    """Remove tabelas e views existentes para garantir uma carga limpa e sem conflitos."""
    print("\n" + "-" * 60)
    print("🧹 Preparando ambiente (Reset limpo do banco)...")
    print("-" * 60)

    tables_to_drop = [
        "fato_internacoes",
        "fato_atendimentos",
        "dim_leito",
        "dim_paciente",
        "dim_convenio",
        "dim_setor",
        "dim_tempo",
    ]

    views_to_drop = [
        "vw_performance_hospitalar",
        "vw_ocupacao_hospitalar",
        "vw_kpi_internacoes",
        "vw_kpi_atendimentos",
    ]

    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        for view in views_to_drop:
            connection.execute(text(f"DROP VIEW IF EXISTS {view};"))
            
        for table in tables_to_drop:
            connection.execute(text(f"DROP TABLE IF EXISTS {table};"))
            
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    
    print("✓ Banco limpo e pronto para novo provisionamento.")


def apply_schemas():
    """Aplica os arquivos DDL de schemas em sql/schemas/"""
    if not SCHEMAS_DIR.exists():
        print(f"⚠️ Diretório de schemas não encontrado: {SCHEMAS_DIR}")
        return

    # Garante que scripts de banco/metabase não sejam processados como schemas do DW
    schema_files = sorted([
        f for f in SCHEMAS_DIR.glob("*.sql") 
        if not f.name.startswith("00_") and "metabase" not in f.name
    ])
    if not schema_files:
        print("⚠️ Nenhum arquivo de schema analítico encontrado.")
        return

    print("\n" + "-" * 60)
    print("📐 [2/6] Aplicando Schemas Estruturais (DDL)...")
    print("-" * 60)

    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for schema_path in schema_files:
            print(f"[*] Aplicando schema: {schema_path.name}...")
            execute_sql_file(connection, schema_path)
            print(f"    ✓ {schema_path.name} criado com sucesso.")
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))


def apply_seeds():
    """Aplica os seeds fixos essenciais (Setores, Convênios)."""
    if not SEEDS_DIR.exists():
        print(f"⚠️ Diretório de seeds não encontrado: {SEEDS_DIR}")
        return

    seed_files = sorted(SEEDS_DIR.glob("*.sql"))
    if not seed_files:
        print("⚠️ Nenhum arquivo de seed encontrado em sql/seeds/.")
        return

    print("\n" + "-" * 60)
    print("🌱 [3/6] Inserindo Seeds Fixos (Convênios e Setores)...")
    print("-" * 60)

    with engine.begin() as connection:
        for seed_path in seed_files:
            print(f"[*] Populando seed: {seed_path.name}...")
            execute_sql_file(connection, seed_path)
            print(f"    ✓ {seed_path.name} carregado com sucesso.")


def apply_views():
    """Compila e aplica as Views analíticas no MySQL para consumo do Metabase."""
    print("\n" + "-" * 60)
    print("📊 [6/6] Compilando Views Analíticas no MySQL...")
    print("-" * 60)

    if not VIEWS_DIR.exists():
        print(f"⚠️ Diretório de views não encontrado: {VIEWS_DIR}")
        return

    view_files = sorted(VIEWS_DIR.glob("*.sql"))
    if not view_files:
        print("⚠️ Nenhum arquivo .sql encontrado em sql/views/.")
        return

    with engine.begin() as connection:
        for view_path in view_files:
            print(f"[*] Compilando view: {view_path.name}...")
            execute_sql_file(connection, view_path)
            print(f"    ✓ {view_path.name} consolidada.")


def main():
    total_start = time.time()
    print("=" * 60)
    print("🏥 HOSPITAL ANALYTICS PLATFORM - PIPELINE ETL & DW")
    print("=" * 60)

    # 1. Espera ativa do banco
    wait_for_mysql()

    # 2. Reset Limpo (Garante idempotência se já foi rodado antes)
    reset_database()

    # 3. Criação das Tabelas DDL
    apply_schemas()

    # 4. Carga dos Seeds
    apply_seeds()

    # 5. Geração e Carga das Dimensões e Fatos Sintéticos
    print("\n" + "-" * 60)
    print("🧪 [4/6 & 5/6] Executando Geradores de Dados Sintéticos...")
    print("-" * 60)

    for step_num, (step_name, script_path) in enumerate(PIPELINE, start=1):
        if not script_path.exists():
            print(f"\n❌ [ERRO CRÍTICO] Script não encontrado: {script_path.name}")
            sys.exit(1)

        print(f"\n[{step_num}/{len(PIPELINE)}] Gerando {step_name} ({script_path.name})...")
        step_start = time.time()

        try:
            runpy.run_path(str(script_path), run_name="__main__")
            elapsed = time.time() - step_start
            print(f"    ✓ {step_name} finalizado em {elapsed:.1f}s.")
        except Exception as e:
            print(f"\n❌ [FALHA] Erro durante a geração de {step_name}: {e}")
            sys.exit(1)

    # 6. Aplicação das Views
    apply_views()

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"🎉 Pipeline concluído com sucesso em {total_elapsed:.1f} segundos!")
    print("🚀 Abra o Metabase em http://localhost:3000 para visualizar os dashboards.")
    print("=" * 60)


if __name__ == "__main__":
    main()