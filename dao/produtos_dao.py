from database.conexao import conectar
from models.produto import Produto

def inserir_produto(produto:Produto):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO produtos (
            codigo_barras,
            nome,
            categoria,
            tamanho,
            cor,
            preco_custo,
            preco_venda,
            estoque,
            ativo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(sql, (
        produto.codigo_barras,
        produto.nome,
        produto.categoria,
        produto.tamanho,
        produto.cor,
        produto.preco_custo,
        produto.preco_venda,
        produto.estoque,
        produto.ativo
    ))

    conexao.commit()
    produto.id = cursor.lastrowid
    conexao.close()

    return produto

def atualizar_produto(produto: Produto):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        UPDATE produtos SET
            codigo_barras = ?,
            nome = ?,
            categoria = ?,
            tamanho = ?,
            cor = ?,
            preco_custo = ?,
            preco_venda = ?,
            estoque = ?,
            ativo = ?
        WHERE id = ?
    """

    cursor.execute(sql, (
        produto.codigo_barras,
        produto.nome,
        produto.categoria,
        produto.tamanho,
        produto.cor,
        produto.preco_custo,
        produto.preco_venda,
        produto.estoque,
        produto.ativo,
        produto.id
    ))

    conexao.commit()
    conexao.close()

def listar_produtos(
    ativos_apenas=True, 
    filtro_nome=None, 
    filtro_categoria=None, 
    filtro_codigo=None,
    filtro_tamanho=None,
    filtro_cor=None,
    preco_min=None,
    preco_max=None,
    estoque_baixo=None,
    ordenar_por="nome",
    ordem_crescente=True
):
    """
    Lista produtos do banco de dados com múltiplas opções de filtros e ordenação.
    
    Parâmetros:
        ativos_apenas (bool): Se True, mostra apenas produtos ativos
        filtro_nome (str): Filtra produtos que contenham este texto no nome
        filtro_categoria (str): Filtra produtos que contenham este texto na categoria
        filtro_codigo (str): Filtra produtos que contenham este texto no código de barras
        filtro_tamanho (str): Filtra produtos que contenham este texto no tamanho
        filtro_cor (str): Filtra produtos que contenham este texto na cor
        preco_min (float): Preço de venda mínimo
        preco_max (float): Preço de venda máximo
        estoque_baixo (int): Se informado, filtra produtos com estoque <= este valor
        ordenar_por (str): Coluna para ordenação (nome, categoria, preco_venda, estoque)
        ordem_crescente (bool): True para crescente, False para decrescente
    
    Retorna:
        lista de objetos Produto ordenados conforme especificado
    
    Exemplos de uso:
        # Buscar produtos com estoque baixo (5 ou menos)
        produtos = listar_produtos(estoque_baixo=5)
        
        # Buscar produtos entre R$ 50 e R$ 100
        produtos = listar_produtos(preco_min=50.0, preco_max=100.0)
        
        # Buscar camisetas azuis, ordenadas por preço decrescente
        produtos = listar_produtos(
            filtro_nome="camiseta", 
            filtro_cor="azul",
            ordenar_por="preco_venda",
            ordem_crescente=False
        )
    """
    conexao = conectar()
    cursor = conexao.cursor()

    # Começa a montar a query SQL
    sql = "SELECT * FROM produtos WHERE 1=1"
    parametros = []

    # Filtro: Produtos ativos/inativos
    if ativos_apenas:
        sql += " AND ativo = 1"
    
    # Filtro: Nome do produto
    if filtro_nome and filtro_nome.strip():
        sql += " AND nome LIKE ?"
        parametros.append(f"%{filtro_nome.strip()}%")
    
    # Filtro: Categoria
    if filtro_categoria and filtro_categoria.strip():
        sql += " AND categoria LIKE ?"
        parametros.append(f"%{filtro_categoria.strip()}%")
    
    # Filtro: Código de barras
    if filtro_codigo and filtro_codigo.strip():
        sql += " AND codigo_barras LIKE ?"
        parametros.append(f"%{filtro_codigo.strip()}%")
    
    # NOVO: Filtro de Tamanho
    if filtro_tamanho and filtro_tamanho.strip():
        sql += " AND tamanho LIKE ?"
        parametros.append(f"%{filtro_tamanho.strip()}%")
    
    # NOVO: Filtro de Cor
    if filtro_cor and filtro_cor.strip():
        sql += " AND cor LIKE ?"
        parametros.append(f"%{filtro_cor.strip()}%")
    
    # NOVO: Filtro de Preço Mínimo
    if preco_min is not None:
        sql += " AND preco_venda >= ?"
        parametros.append(preco_min)
    
    # NOVO: Filtro de Preço Máximo
    if preco_max is not None:
        sql += " AND preco_venda <= ?"
        parametros.append(preco_max)
    
    # NOVO: Filtro de Estoque Baixo
    if estoque_baixo is not None:
        sql += " AND estoque <= ?"
        parametros.append(estoque_baixo)
    
    # NOVO: Ordenação
    # Valida a coluna para evitar SQL injection
    colunas_validas = ["nome", "categoria", "preco_venda", "estoque", "tamanho", "cor", "preco_custo"]
    if ordenar_por not in colunas_validas:
        ordenar_por = "nome"
    
    direcao = "ASC" if ordem_crescente else "DESC"
    sql += f" ORDER BY {ordenar_por} {direcao}"

    # Executa a query
    cursor.execute(sql, parametros)
    linhas = cursor.fetchall()
    conexao.close()

    # Converte as linhas do banco em objetos Produto
    produtos = []
    for linha in linhas:
        produtos.append(_linha_para_produto(linha))

    return produtos

def buscar_produto_por_id(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM produtos WHERE id = ?",
        (produto_id,)
    )

    linha = cursor.fetchone()
    conexao.close()

    if linha:
        return _linha_para_produto(linha)
    
    return None

def buscar_produto_por_codigo_barras(codigo_barras):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM produtos WHERE codigo_barras = ? AND ativo = 1",
        (codigo_barras,)
    )

    linha = cursor.fetchone()
    conexao.close()

    if linha:
        return _linha_para_produto(linha)

    return None

def desativar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE produtos SET ativo = 0 WHERE id = ?",
        (produto_id,)
    )

    conexao.commit()
    conexao.close()

def reativar_produto(produto_id):
    """
    Reativa um produto que estava desativado.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE produtos SET ativo = 1 WHERE id = ?",
        (produto_id,)
    )

    conexao.commit()
    conexao.close()

# =========================
# Função auxiliar interna
# =========================

def _linha_para_produto(linha):
    return Produto(
        id=linha["id"],
        codigo_barras=linha["codigo_barras"],
        nome=linha["nome"],
        categoria=linha["categoria"],
        tamanho=linha["tamanho"],
        cor=linha["cor"],
        preco_custo=linha["preco_custo"],
        preco_venda=linha["preco_venda"],
        estoque=linha["estoque"],
        ativo=linha["ativo"]
    )