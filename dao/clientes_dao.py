from banco.conexao import conectar
from modelos.cliente import Cliente
from datetime import datetime


def inserir_cliente(cliente: Cliente):
    """
    Cadastra um novo cliente no banco de dados.
    
    Args:
        cliente: Objeto Cliente com os dados do cliente
        
    Returns:
        O objeto Cliente com o ID preenchido
        
    Raises:
        ValueError: Se o nome não foi informado ou CPF/CNPJ já existe
        
    Exemplo:
        cliente = Cliente(
            nome="Maria Santos",
            telefone="(86) 98888-8888",
            email="maria@email.com"
        )
        cliente_cadastrado = inserir_cliente(cliente)
        print(f"Cliente cadastrado com ID: {cliente_cadastrado.id}")
    """
    if not cliente.nome or not cliente.nome.strip():
        raise ValueError("O nome do cliente é obrigatório.")
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Define a data de cadastro se não foi informada
    if not cliente.data_cadastro:
        cliente.data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO clientes (
                nome,
                cpf_cnpj,
                telefone,
                email,
                endereco,
                cidade,
                estado,
                cep,
                observacoes,
                data_cadastro,
                ativo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente.nome,
            cliente.cpf_cnpj,
            cliente.telefone,
            cliente.email,
            cliente.endereco,
            cliente.cidade,
            cliente.estado,
            cliente.cep,
            cliente.observacoes,
            cliente.data_cadastro,
            cliente.ativo
        ))
        
        conexao.commit()
        cliente.id = cursor.lastrowid
        
        return cliente
        
    except Exception as e:
        conexao.rollback()
        # Se for erro de CPF/CNPJ duplicado
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Este CPF/CNPJ já está cadastrado.")
        raise e
        
    finally:
        conexao.close()


def atualizar_cliente(cliente: Cliente):
    """
    Atualiza os dados de um cliente existente.
    
    Args:
        cliente: Objeto Cliente com os dados atualizados (deve ter ID)
        
    Raises:
        ValueError: Se o ID não foi informado ou cliente não existe
    """
    if not cliente.id:
        raise ValueError("O ID do cliente é obrigatório para atualização.")
    
    if not cliente.nome or not cliente.nome.strip():
        raise ValueError("O nome do cliente é obrigatório.")
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            UPDATE clientes SET
                nome = ?,
                cpf_cnpj = ?,
                telefone = ?,
                email = ?,
                endereco = ?,
                cidade = ?,
                estado = ?,
                cep = ?,
                observacoes = ?,
                ativo = ?
            WHERE id = ?
        """, (
            cliente.nome,
            cliente.cpf_cnpj,
            cliente.telefone,
            cliente.email,
            cliente.endereco,
            cliente.cidade,
            cliente.estado,
            cliente.cep,
            cliente.observacoes,
            cliente.ativo,
            cliente.id
        ))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Cliente com ID {cliente.id} não encontrado.")
        
        conexao.commit()
        
    except Exception as e:
        conexao.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Este CPF/CNPJ já está cadastrado para outro cliente.")
        raise e
        
    finally:
        conexao.close()


def buscar_cliente_por_id(cliente_id):
    """
    Busca um cliente pelo ID.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        Objeto Cliente ou None se não encontrar
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    linha = cursor.fetchone()
    conexao.close()
    
    if linha:
        return _linha_para_cliente(linha)
    
    return None


def buscar_cliente_por_cpf_cnpj(cpf_cnpj):
    """
    Busca um cliente pelo CPF ou CNPJ.
    
    Args:
        cpf_cnpj: CPF ou CNPJ do cliente
        
    Returns:
        Objeto Cliente ou None se não encontrar
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "SELECT * FROM clientes WHERE cpf_cnpj = ? AND ativo = 1",
        (cpf_cnpj,)
    )
    linha = cursor.fetchone()
    conexao.close()
    
    if linha:
        return _linha_para_cliente(linha)
    
    return None


def listar_clientes(
    ativos_apenas=True,
    filtro_nome=None,
    filtro_cpf_cnpj=None,
    filtro_telefone=None,
    ordenar_por="nome",
    ordem_crescente=True
):
    """
    Lista clientes com opções de filtros.
    
    Args:
        ativos_apenas: Se True, mostra apenas clientes ativos
        filtro_nome: Filtra por nome (busca parcial)
        filtro_cpf_cnpj: Filtra por CPF/CNPJ (busca parcial)
        filtro_telefone: Filtra por telefone (busca parcial)
        ordenar_por: Coluna para ordenação (nome, cidade, data_cadastro)
        ordem_crescente: True para crescente, False para decrescente
        
    Returns:
        Lista de objetos Cliente
        
    Exemplo:
        # Buscar clientes com "Silva" no nome
        clientes = listar_clientes(filtro_nome="Silva")
        
        # Buscar todos os clientes, incluindo inativos
        todos = listar_clientes(ativos_apenas=False)
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = "SELECT * FROM clientes WHERE 1=1"
    parametros = []
    
    # Filtro: Clientes ativos/inativos
    if ativos_apenas:
        sql += " AND ativo = 1"
    
    # Filtro: Nome
    if filtro_nome and filtro_nome.strip():
        sql += " AND nome LIKE ?"
        parametros.append(f"%{filtro_nome.strip()}%")
    
    # Filtro: CPF/CNPJ
    if filtro_cpf_cnpj and filtro_cpf_cnpj.strip():
        sql += " AND cpf_cnpj LIKE ?"
        parametros.append(f"%{filtro_cpf_cnpj.strip()}%")
    
    # Filtro: Telefone
    if filtro_telefone and filtro_telefone.strip():
        sql += " AND telefone LIKE ?"
        parametros.append(f"%{filtro_telefone.strip()}%")
    
    # Ordenação
    colunas_validas = ["nome", "cidade", "data_cadastro", "cpf_cnpj"]
    if ordenar_por not in colunas_validas:
        ordenar_por = "nome"
    
    direcao = "ASC" if ordem_crescente else "DESC"
    sql += f" ORDER BY {ordenar_por} {direcao}"
    
    cursor.execute(sql, parametros)
    linhas = cursor.fetchall()
    conexao.close()
    
    clientes = []
    for linha in linhas:
        clientes.append(_linha_para_cliente(linha))
    
    return clientes


def desativar_cliente(cliente_id):
    """
    Desativa um cliente (soft delete).
    O cliente não será excluído, apenas marcado como inativo.
    
    Args:
        cliente_id: ID do cliente a ser desativado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "UPDATE clientes SET ativo = 0 WHERE id = ?",
        (cliente_id,)
    )
    
    conexao.commit()
    conexao.close()


def reativar_cliente(cliente_id):
    """
    Reativa um cliente que estava desativado.
    
    Args:
        cliente_id: ID do cliente a ser reativado
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute(
        "UPDATE clientes SET ativo = 1 WHERE id = ?",
        (cliente_id,)
    )
    
    conexao.commit()
    conexao.close()


def obter_total_clientes_ativos():
    """
    Retorna o total de clientes ativos no sistema.
    
    Returns:
        int: Número de clientes ativos
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE ativo = 1")
    resultado = cursor.fetchone()
    conexao.close()
    
    return resultado["total"]


def obter_historico_compras_cliente(cliente_id):
    """
    Retorna o histórico de compras de um cliente.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        Lista de dicionários com informações das vendas:
        - venda_id: ID da venda
        - data: Data da venda
        - total: Valor total
        - forma_pagamento: Como pagou
        
    Exemplo:
        historico = obter_historico_compras_cliente(1)
        for venda in historico:
            print(f"Venda #{venda['venda_id']} - R$ {venda['total']:.2f}")
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT 
            id as venda_id,
            data,
            total,
            forma_pagamento,
            desconto
        FROM vendas
        WHERE cliente_id = ?
        AND cancelada = 0
        ORDER BY data DESC
    """, (cliente_id,))
    
    linhas = cursor.fetchall()
    conexao.close()
    
    # Converte Row para dicionário
    historico = []
    for linha in linhas:
        historico.append({
            "venda_id": linha["venda_id"],
            "data": linha["data"],
            "total": linha["total"],
            "forma_pagamento": linha["forma_pagamento"],
            "desconto": linha["desconto"]
        })
    
    return historico


def obter_total_gasto_cliente(cliente_id):
    """
    Calcula o total que um cliente já gastou na loja.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        float: Valor total gasto pelo cliente
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) as total_gasto
        FROM vendas
        WHERE cliente_id = ?
        AND cancelada = 0
    """, (cliente_id,))
    
    resultado = cursor.fetchone()
    conexao.close()
    
    return resultado["total_gasto"]


# =========================
# Função auxiliar interna
# =========================

def _linha_para_cliente(linha):
    """
    Converte uma linha do banco em um objeto Cliente.
    
    Args:
        linha: Row do SQLite
        
    Returns:
        Cliente: Objeto Cliente
    """
    return Cliente(
        id=linha["id"],
        nome=linha["nome"],
        cpf_cnpj=linha["cpf_cnpj"],
        telefone=linha["telefone"],
        email=linha["email"],
        endereco=linha["endereco"],
        cidade=linha["cidade"],
        estado=linha["estado"],
        cep=linha["cep"],
        observacoes=linha["observacoes"],
        data_cadastro=linha["data_cadastro"],
        ativo=linha["ativo"]
    )