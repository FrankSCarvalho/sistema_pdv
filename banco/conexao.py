import sqlite3
import os

#Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminho do Banco e do script SQL
CAMINHO_BANCO = os.path.join(BASE_DIR, "estoque.db")
CAMINHO_SCRIPT = os.path.join(BASE_DIR, "banco", "init_db.sql")


def conectar():
    """
    Cria e retorna uma conexão com o banco SQLite,
    garantindo que o banco esteja inicializado.
    """

    banco_existe = os.path.exists(CAMINHO_BANCO)

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row # acesso por nome da coluna

    ativar_foreign_keys(conexao)

    if not banco_existe:
        inicializar_banco(conexao)

    return conexao

def ativar_foreign_keys(conexao):
    """
    Ativa o suporte a chaves estrangeiras no SQLite.
    """
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    conexao.commit()

def inicializar_banco(conexao):
    """
    Executa o script SQL de inicialização do banco.
    """
    if not os.path.exists(CAMINHO_SCRIPT):
        raise FileNotFoundError("Arquivo init_db.sql não encontrado.")
    
    with open(CAMINHO_SCRIPT, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    conexao.executescript(script_sql)
    conexao.commit()

    print("Banco de dados inicializado com sucesso!")