from database.conexao import conectar
from dao.produtos_dao import buscar_produto_por_id
from datetime import datetime


def registrar_entrada(produto_id, quantidade, observacao=None):
    """
    Registra uma entrada de estoque para um produto.
    """
    if quantidade <=0:
        raise ValueError("A quantidade deve ser maior que zero.")
    
    conexao = conectar()
    cursor = conexao.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Registra movimentação
    cursor.execute("""
        INSERT INTO movimentacoes_estoque (
            produto_id,
            tipo,
            quantidade,
            data,
            observacao
        ) VALUES (?, 'ENTRADA', ?, ?, ?)
    """, (produto_id, quantidade, data_atual, observacao))

    # Atualiza estoque do produto
    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque + ?
        WHERE id = ?
    """, (quantidade, produto_id))

    conexao.commit()
    conexao.close()

def registrar_saida(produto_id, quantidade, observacao=None):
    """
    Registra uma saída de estoque para um produto.
    """
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    produto = buscar_produto_por_id(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado.")

    if produto.estoque < quantidade:
        raise ValueError("Estoque insuficiente.")

    conexao = conectar()
    cursor = conexao.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Registra movimentação
    cursor.execute("""
        INSERT INTO movimentacoes_estoque (
            produto_id,
            tipo,
            quantidade,
            data,
            observacao
        ) VALUES (?, 'SAIDA', ?, ?, ?)
    """, (produto_id, quantidade, data_atual, observacao))

    # Atualiza estoque do produto
    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - ?
        WHERE id = ?
    """, (quantidade, produto_id))

    conexao.commit()
    conexao.close()

def listar_movimentacoes(produto_id=None):
    """
    Lista movimentações de estoque.
    Se produto_id for informado, filtra pelo produto.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    if produto_id:
        cursor.execute("""
            SELECT m.id, m.tipo, m.quantidade, m.data, m.observacao,
                   p.nome, p.tamanho, p.cor
            FROM movimentacoes_estoque m
            JOIN produtos p ON p.id = m.produto_id
            WHERE p.id = ?
            ORDER BY m.data DESC
        """, (produto_id,))
    else:
        cursor.execute("""
            SELECT m.id, m.tipo, m.quantidade, m.data, m.observacao,
                   p.nome, p.tamanho, p.cor
            FROM movimentacoes_estoque m
            JOIN produtos p ON p.id = m.produto_id
            ORDER BY m.data DESC
        """)

    movimentacoes = cursor.fetchall()
    conexao.close()

    return movimentacoes
