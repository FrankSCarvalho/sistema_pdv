import sqlite3
import os
import sys


def caminho_base():
    """
    Retorna o diretório base do projeto ou do executável.
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pasta_dados_usuario():
    """
    Pasta correta para salvar dados persistentes.
    """
    if os.name == "nt":  # Windows
        base = os.getenv("LOCALAPPDATA")
        return os.path.join(base, "EstoqueLoja")
    else:  # Linux / macOS
        base = os.path.expanduser("~/.local/share")
        return os.path.join(base, "estoque_loja")


BASE_DIR = caminho_base()
PASTA_DADOS = pasta_dados_usuario()

os.makedirs(PASTA_DADOS, exist_ok=True)

CAMINHO_BANCO = os.path.join(PASTA_DADOS, "estoque.db")
CAMINHO_SCRIPT = os.path.join(BASE_DIR, "banco", "init_db.sql")


def conectar():
    """
    Cria e retorna uma conexão com o banco SQLite,
    garantindo que o banco esteja inicializado.
    """
    banco_existe = os.path.exists(CAMINHO_BANCO)

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

    ativar_foreign_keys(conexao)

    if not banco_existe:
        inicializar_banco(conexao)

    return conexao


def ativar_foreign_keys(conexao):
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    conexao.commit()


def inicializar_banco(conexao):
    if not os.path.exists(CAMINHO_SCRIPT):
        raise FileNotFoundError("Arquivo init_db.sql não encontrado.")

    with open(CAMINHO_SCRIPT, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    conexao.executescript(script_sql)
    conexao.commit()
