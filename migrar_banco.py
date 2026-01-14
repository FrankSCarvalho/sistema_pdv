"""
Script de migração do banco de dados.
Adiciona a tabela de usuários ao banco existente.

Execute este script UMA VEZ para atualizar seu banco de dados existente.
"""

import sqlite3
import os
import sys
from datetime import datetime

def caminho_base():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def pasta_dados_usuario():
    if os.name == "nt": 
        base = os.getenv("LOCALAPPDATA")
        return os.path.join(base, "EstoqueLoja")
    else: 
        base = os.path.expanduser("~/.local/share")
        return os.path.join(base, "estoque_loja")

PASTA_DADOS = pasta_dados_usuario()
CAMINHO_BANCO = os.path.join(PASTA_DADOS, "estoque.db")


def verificar_tabela_existe(conexao, nome_tabela):
    """Verifica se uma tabela existe no banco."""
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (nome_tabela,)
    )
    return cursor.fetchone() is not None


def migrar_banco():
    """Executa a migração do banco de dados."""
    
    print("=" * 60)
    print("MIGRAÇÃO DO BANCO DE DADOS - Sistema PDV v2.0.0")
    print("=" * 60)
    print()
    
    # Verifica se o banco existe
    if not os.path.exists(CAMINHO_BANCO):
        print(f"❌ Banco de dados não encontrado em: {CAMINHO_BANCO}")
        print("   Execute o sistema primeiro para criar o banco.")
        return False
    
    print(f"✓ Banco de dados encontrado: {CAMINHO_BANCO}")
    
    # Faz backup
    backup_path = CAMINHO_BANCO + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copy2(CAMINHO_BANCO, backup_path)
        print(f"✓ Backup criado: {backup_path}")
    except Exception as e:
        print(f"⚠ Aviso: Não foi possível criar backup: {e}")
    
    # Conecta ao banco
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        
        print("✓ Conectado ao banco de dados")
        
        # Verifica se a tabela usuarios já existe
        if verificar_tabela_existe(conexao, "usuarios"):
            print("⚠ A tabela 'usuarios' já existe. Migração não necessária.")
            conexao.close()
            return True
        
        print()
        print("Criando tabela de usuários...")
        
        # Cria a tabela usuarios
        cursor.execute("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nivel_acesso INTEGER NOT NULL DEFAULT 3,
                ativo INTEGER NOT NULL DEFAULT 1,
                data_criacao TEXT NOT NULL,
                ultimo_acesso TEXT
            )
        """)
        
        # Cria índices
        cursor.execute("CREATE INDEX idx_usuarios_login ON usuarios(login)")
        cursor.execute("CREATE INDEX idx_usuarios_nivel_acesso ON usuarios(nivel_acesso)")
        
        print("✓ Tabela 'usuarios' criada")
        
        # Adiciona coluna usuario_id nas tabelas existentes (se não existir)
        print()
        print("Atualizando tabelas existentes...")
        
        # Verifica se a coluna usuario_id já existe em vendas
        cursor.execute("PRAGMA table_info(vendas)")
        colunas_vendas = [col[1] for col in cursor.fetchall()]
        
        if "usuario_id" not in colunas_vendas:
            cursor.execute("""
                ALTER TABLE vendas 
                ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)
            """)
            cursor.execute("CREATE INDEX idx_vendas_usuario_id ON vendas(usuario_id)")
            print("✓ Coluna 'usuario_id' adicionada à tabela 'vendas'")
        else:
            print("⚠ Coluna 'usuario_id' já existe na tabela 'vendas'")
        
        # Verifica se a coluna usuario_id já existe em movimentacoes_estoque
        cursor.execute("PRAGMA table_info(movimentacoes_estoque)")
        colunas_mov = [col[1] for col in cursor.fetchall()]
        
        if "usuario_id" not in colunas_mov:
            cursor.execute("""
                ALTER TABLE movimentacoes_estoque 
                ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)
            """)
            cursor.execute("CREATE INDEX idx_mov_estoque_usuario ON movimentacoes_estoque(usuario_id)")
            print("✓ Coluna 'usuario_id' adicionada à tabela 'movimentacoes_estoque'")
        else:
            print("⚠ Coluna 'usuario_id' já existe na tabela 'movimentacoes_estoque'")
        
        # Cria usuário administrador padrão
        print()
        print("Criando usuário administrador padrão...")
        
        import hashlib
        senha_hash = hashlib.sha256("admin123".encode('utf-8')).hexdigest()
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO usuarios (nome, login, senha_hash, nivel_acesso, ativo, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Administrador", "admin", senha_hash, 1, 1, data_atual))
        
        print("✓ Usuário administrador criado")
        print("   Login: admin")
        print("   Senha: admin123")
        print("   ⚠ IMPORTANTE: Altere a senha após o primeiro login!")
        
        # Commit das alterações
        conexao.commit()
        conexao.close()
        
        print()
        print("=" * 60)
        print("✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. Execute o sistema com: python main_com_login.py")
        print("2. Faça login com: admin / admin123")
        print("3. Altere a senha do administrador")
        print("4. Crie usuários para sua equipe")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO NA MIGRAÇÃO!")
        print("=" * 60)
        print(f"Erro: {e}")
        print()
        print("O backup foi salvo em:", backup_path)
        print("Você pode restaurá-lo se necessário.")
        
        if 'conexao' in locals():
            conexao.rollback()
            conexao.close()
        
        return False


if __name__ == "__main__":
    print()
    input("Pressione ENTER para iniciar a migração...")
    print()
    
    sucesso = migrar_banco()
    
    print()
    input("Pressione ENTER para sair...")
    
    sys.exit(0 if sucesso else 1)
