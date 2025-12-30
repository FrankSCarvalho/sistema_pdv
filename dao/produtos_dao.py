from banco.conexao import conectar
from modelos.produto import Produto

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

def listar_produtos(ativos_apenas=True):
    conexao = conectar()
    cursor = conexao.cursor()

    if ativos_apenas:
        sql = "SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome"
        cursor.execute(sql)
    else:
        sql = "SELECT * FROM produtos ORDER BY nome"
        cursor.execute(sql)

    linhas = cursor.fetchall()
    conexao.close()

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