import sqlite3
import os
import sys

def caminho_base():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def pasta_dados_usuario():
    if os.name == "nt": 
        base = os.getenv("LOCALAPPDATA")
        return os.path.join(base, "EstoqueLoja")
    else: 
        base = os.path.expanduser("~/.local/share")
        return os.path.join(base, "estoque_loja")

BASE_DIR = caminho_base()
PASTA_DADOS = pasta_dados_usuario()
os.makedirs(PASTA_DADOS, exist_ok=True)

CAMINHO_BANCO = os.path.join(PASTA_DADOS, "estoque.db")
CAMINHO_SCRIPT = os.path.join(BASE_DIR, "banco", "init_db.sql")

def conectar():
    """
    Conecta ao banco e garante que as tabelas existam.
    """
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    
    # Ativa chaves estrangeiras
    conexao.execute("PRAGMA foreign_keys = ON;")

    # VERIFICAÇÃO REAL: A tabela clientes existe?
    cursor = conexao.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
    tabela_existe = cursor.fetchone()

    if not tabela_existe:
        print("Tabela 'clientes' não encontrada. Inicializando banco...")
        inicializar_banco(conexao)
    
    return conexao

def inicializar_banco(conexao):
    if not os.path.exists(CAMINHO_SCRIPT):
        raise FileNotFoundError(f"Arquivo init_db.sql não encontrado em: {CAMINHO_SCRIPT}")

    with open(CAMINHO_SCRIPT, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    try:
        # O executescript pode rodar várias instruções de uma vez
        conexao.executescript(script_sql)
        conexao.commit()
        print("Tabelas criadas e banco inicializado com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao executar o script SQL: {e}")
        raise e