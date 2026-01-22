from database.conexao import conectar
from models.usuario import Usuario
from datetime import datetime


def inserir_usuario(usuario: Usuario):
    """
    Cadastra um novo usuário no sistema.
    
    Args:
        usuario: Objeto Usuario com os dados
        
    Returns:
        Usuario: O objeto com ID preenchido
        
    Raises:
        ValueError: Se o login já existir ou dados inválidos
    """
    if not usuario.nome or not usuario.nome.strip():
        raise ValueError("O nome do usuário é obrigatório.")
    
    if not usuario.login or not usuario.login.strip():
        raise ValueError("O login é obrigatório.")
    
    if not usuario.senha_hash:
        raise ValueError("A senha é obrigatória.")
    
    if usuario.nivel_acesso not in [1, 2, 3]:
        raise ValueError("Nível de acesso inválido.")
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Define a data de criação se não foi informada
    if not usuario.data_criacao:
        usuario.data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (
                nome,
                login,
                senha_hash,
                nivel_acesso,
                ativo,
                data_criacao
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            usuario.nome,
            usuario.login.lower(),  # Login sempre em minúsculas
            usuario.senha_hash,
            usuario.nivel_acesso,
            usuario.ativo,
            usuario.data_criacao
        ))
        
        conexao.commit()
        usuario.id = cursor.lastrowid
        
        return usuario
        
    except Exception as e:
        conexao.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Este login já está cadastrado.")
        raise e
        
    finally:
        conexao.close()


def atualizar_usuario(usuario: Usuario):
    """
    Atualiza os dados de um usuário existente.
    
    Args:
        usuario: Objeto Usuario com os dados atualizados
        
    Raises:
        ValueError: Se o ID não foi informado ou usuário não existe
    """
    if not usuario.id:
        raise ValueError("O ID do usuário é obrigatório para atualização.")
    
    if not usuario.nome or not usuario.nome.strip():
        raise ValueError("O nome do usuário é obrigatório.")
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            UPDATE usuarios SET
                nome = ?,
                login = ?,
                senha_hash = ?,
                nivel_acesso = ?,
                ativo = ?
            WHERE id = ?
        """, (
            usuario.nome,
            usuario.login.lower(),
            usuario.senha_hash,
            usuario.nivel_acesso,
            usuario.ativo,
            usuario.id
        ))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Usuário com ID {usuario.id} não encontrado.")
        
        conexao.commit()
        
    except Exception as e:
        conexao.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Este login já está cadastrado para outro usuário.")
        raise e
        
    finally:
        conexao.close()


def buscar_usuario_por_id(usuario_id):
    """
    Busca um usuário pelo ID.
    
    Args:
        usuario_id: ID do usuário
        
    Returns:
        Usuario ou None: Objeto Usuario se encontrado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    linha = cursor.fetchone()
    conexao.close()
    
    if linha:
        return _linha_para_usuario(linha)
    
    return None


def buscar_usuario_por_login(login):
    """
    Busca um usuário pelo login.
    
    Args:
        login: Login do usuário
        
    Returns:
        Usuario ou None: Objeto Usuario se encontrado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "SELECT * FROM usuarios WHERE login = ? AND ativo = 1",
        (login.lower(),)
    )
    linha = cursor.fetchone()
    conexao.close()
    
    if linha:
        return _linha_para_usuario(linha)
    
    return None


def autenticar_usuario(login, senha):
    """
    Autentica um usuário pelo login e senha.
    
    Args:
        login: Login do usuário
        senha: Senha em texto plano
        
    Returns:
        Usuario ou None: Objeto Usuario se autenticado com sucesso
    """
    usuario = buscar_usuario_por_login(login)
    
    if usuario and usuario.verificar_senha(senha):
        # Atualiza último acesso
        atualizar_ultimo_acesso(usuario.id)
        return usuario
    
    return None


def atualizar_ultimo_acesso(usuario_id):
    """
    Atualiza a data/hora do último acesso do usuário.
    
    Args:
        usuario_id: ID do usuário
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?",
        (data_atual, usuario_id)
    )
    
    conexao.commit()
    conexao.close()


def listar_usuarios(ativos_apenas=True, filtro_nome=None):
    """
    Lista usuários do sistema.
    
    Args:
        ativos_apenas: Se True, mostra apenas usuários ativos
        filtro_nome: Filtra por nome (busca parcial)
        
    Returns:
        List[Usuario]: Lista de usuários
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = "SELECT * FROM usuarios WHERE 1=1"
    parametros = []
    
    if ativos_apenas:
        sql += " AND ativo = 1"
    
    if filtro_nome and filtro_nome.strip():
        sql += " AND nome LIKE ?"
        parametros.append(f"%{filtro_nome.strip()}%")
    
    sql += " ORDER BY nome ASC"
    
    cursor.execute(sql, parametros)
    linhas = cursor.fetchall()
    conexao.close()
    
    usuarios = []
    for linha in linhas:
        usuarios.append(_linha_para_usuario(linha))
    
    return usuarios


def desativar_usuario(usuario_id):
    """
    Desativa um usuário (soft delete).
    
    Args:
        usuario_id: ID do usuário a ser desativado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "UPDATE usuarios SET ativo = 0 WHERE id = ?",
        (usuario_id,)
    )
    
    conexao.commit()
    conexao.close()


def reativar_usuario(usuario_id):
    """
    Reativa um usuário que estava desativado.
    
    Args:
        usuario_id: ID do usuário a ser reativado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "UPDATE usuarios SET ativo = 1 WHERE id = ?",
        (usuario_id,)
    )
    
    conexao.commit()
    conexao.close()


def alterar_senha(usuario_id, senha_nova):
    """
    Altera a senha de um usuário.
    
    Args:
        usuario_id: ID do usuário
        senha_nova: Nova senha em texto plano
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    senha_hash = Usuario.gerar_hash_senha(senha_nova)
    
    cursor.execute(
        "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
        (senha_hash, usuario_id)
    )
    
    conexao.commit()
    conexao.close()


def criar_usuario_admin_padrao():
    """
    Cria um usuário administrador padrão se não existir nenhum usuário no sistema.
    Login: admin
    Senha: admin123
    
    Returns:
        bool: True se o usuário foi criado, False se já existem usuários
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Verifica se já existem usuários
    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    total = cursor.fetchone()["total"]
    conexao.close()
    
    if total > 0:
        return False
    
    # Cria usuário admin padrão
    admin = Usuario(
        nome="Administrador",
        login="admin",
        senha_hash=Usuario.gerar_hash_senha("admin123"),
        nivel_acesso=Usuario.ADMINISTRADOR,
        ativo=1
    )
    
    inserir_usuario(admin)
    return True


# =========================
# Função auxiliar interna
# =========================

def _linha_para_usuario(linha):
    """
    Converte uma linha do banco em um objeto Usuario.
    
    Args:
        linha: Row do SQLite
        
    Returns:
        Usuario: Objeto Usuario
    """
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        login=linha["login"],
        senha_hash=linha["senha_hash"],
        nivel_acesso=linha["nivel_acesso"],
        ativo=linha["ativo"],
        data_criacao=linha["data_criacao"],
        ultimo_acesso=linha["ultimo_acesso"]
    )
