from banco.conexao import conectar
from modelos.venda import Venda, ItemVenda
from datetime import datetime


def registrar_venda(venda: Venda):
    """
    Registra uma nova venda no banco de dados.
    
    Esta função faz 3 coisas importantes:
    1. Salva a venda (tabela vendas)
    2. Salva os itens da venda (tabela itens_venda)
    3. Dá baixa no estoque dos produtos vendidos
    
    Args:
        venda: Objeto Venda com os dados da venda e seus itens
        
    Returns:
        O ID da venda criada
        
    Raises:
        ValueError: Se a venda não tiver itens ou houver estoque insuficiente
        
    Exemplo:
        from modelos.venda import Venda, ItemVenda
        
        # Criar uma venda
        venda = Venda(
            total=150.0,
            forma_pagamento="DINHEIRO"
        )
        
        # Adicionar itens
        venda.itens.append(ItemVenda(
            produto_id=1,
            quantidade=2,
            preco_unitario=50.0,
            subtotal=100.0
        ))
        
        # Registrar no banco
        venda_id = registrar_venda(venda)
    """
    if not venda.itens:
        raise ValueError("A venda deve ter pelo menos um item.")
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Define a data atual se não foi informada
        if not venda.data:
            venda.data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. INSERIR A VENDA (cabeçalho)
        cursor.execute("""
            INSERT INTO vendas (
                data,
                total,
                desconto,
                forma_pagamento,
                observacao,
                cliente_id,
                usuario_id,
                cancelada
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            venda.data,
            venda.total,
            venda.desconto,
            venda.forma_pagamento,
            venda.observacao,
            venda.cliente_id,
            venda.usuario_id,
            venda.cancelada
        ))
        
        venda_id = cursor.lastrowid
        
        # 2. INSERIR OS ITENS DA VENDA
        for item in venda.itens:
            # Verifica se há estoque suficiente
            cursor.execute("SELECT estoque FROM produtos WHERE id = ?", (item.produto_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"Produto ID {item.produto_id} não encontrado.")
            
            estoque_atual = resultado["estoque"]
            
            if estoque_atual < item.quantidade:
                raise ValueError(
                    f"Estoque insuficiente para o produto ID {item.produto_id}. "
                    f"Estoque atual: {estoque_atual}, solicitado: {item.quantidade}"
                )
            
            # Insere o item da venda
            cursor.execute("""
                INSERT INTO itens_venda (
                    venda_id,
                    produto_id,
                    quantidade,
                    preco_unitario,
                    subtotal
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                venda_id,
                item.produto_id,
                item.quantidade,
                item.preco_unitario,
                item.subtotal
            ))
            
            # 3. DÁ BAIXA NO ESTOQUE
            cursor.execute("""
                UPDATE produtos
                SET estoque = estoque - ?
                WHERE id = ?
            """, (item.quantidade, item.produto_id))
        
        # Commit de tudo de uma vez
        conexao.commit()
        
        return venda_id
        
    except Exception as e:
        # Se der erro, desfaz tudo (rollback)
        conexao.rollback()
        raise e
        
    finally:
        conexao.close()


def buscar_venda_por_id(venda_id):
    """
    Busca uma venda pelo ID, incluindo todos os seus itens.
    
    Args:
        venda_id: ID da venda
        
    Returns:
        Objeto Venda com todos os itens ou None se não encontrar
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Busca a venda
    cursor.execute("SELECT * FROM vendas WHERE id = ?", (venda_id,))
    linha_venda = cursor.fetchone()
    
    if not linha_venda:
        conexao.close()
        return None
    
    # Cria o objeto Venda
    venda = Venda(
        id=linha_venda["id"],
        data=linha_venda["data"],
        total=linha_venda["total"],
        desconto=linha_venda["desconto"],
        forma_pagamento=linha_venda["forma_pagamento"],
        observacao=linha_venda["observacao"],
        cliente_id=linha_venda["cliente_id"],
        usuario_id=linha_venda["usuario_id"],
        cancelada=linha_venda["cancelada"]
    )
    
    # Busca os itens da venda com informações do produto
    cursor.execute("""
        SELECT 
            iv.*,
            p.nome as produto_nome,
            p.tamanho,
            p.cor
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        WHERE iv.venda_id = ?
    """, (venda_id,))
    
    linhas_itens = cursor.fetchall()
    conexao.close()
    
    # Adiciona os itens à venda
    for linha in linhas_itens:
        item = ItemVenda(
            id=linha["id"],
            venda_id=linha["venda_id"],
            produto_id=linha["produto_id"],
            quantidade=linha["quantidade"],
            preco_unitario=linha["preco_unitario"],
            subtotal=linha["subtotal"],
            produto_nome=f"{linha['produto_nome']} ({linha['tamanho']} {linha['cor']})"
        )
        venda.itens.append(item)
    
    return venda


def listar_vendas(data_inicial=None, data_final=None, incluir_canceladas=False):
    """
    Lista vendas com opção de filtrar por período.
    
    Args:
        data_inicial: Data inicial no formato "YYYY-MM-DD" (opcional)
        data_final: Data final no formato "YYYY-MM-DD" (opcional)
        incluir_canceladas: Se True, mostra vendas canceladas também
        
    Returns:
        Lista de objetos Venda (sem os itens, apenas o cabeçalho)
        
    Exemplo:
        # Listar todas as vendas de hoje
        from datetime import date
        hoje = date.today().strftime("%Y-%m-%d")
        vendas = listar_vendas(data_inicial=hoje, data_final=hoje)
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = "SELECT * FROM vendas WHERE 1=1"
    parametros = []
    
    # Filtro por cancelada
    if not incluir_canceladas:
        sql += " AND cancelada = 0"
    
    # Filtro por data inicial
    if data_inicial:
        sql += " AND date(data) >= ?"
        parametros.append(data_inicial)
    
    # Filtro por data final
    if data_final:
        sql += " AND date(data) <= ?"
        parametros.append(data_final)
    
    sql += " ORDER BY data DESC"
    
    cursor.execute(sql, parametros)
    linhas = cursor.fetchall()
    conexao.close()
    
    vendas = []
    for linha in linhas:
        venda = Venda(
            id=linha["id"],
            data=linha["data"],
            total=linha["total"],
            desconto=linha["desconto"],
            forma_pagamento=linha["forma_pagamento"],
            observacao=linha["observacao"],
            cliente_id=linha["cliente_id"],
            usuario_id=linha["usuario_id"],
            cancelada=linha["cancelada"]
        )
        vendas.append(venda)
    
    return vendas


def cancelar_venda(venda_id):
    """
    Cancela uma venda e devolve os produtos ao estoque.
    
    Args:
        venda_id: ID da venda a ser cancelada
        
    Raises:
        ValueError: Se a venda não existir ou já estiver cancelada
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Verifica se a venda existe e não está cancelada
        cursor.execute(
            "SELECT cancelada FROM vendas WHERE id = ?",
            (venda_id,)
        )
        resultado = cursor.fetchone()
        
        if not resultado:
            raise ValueError("Venda não encontrada.")
        
        if resultado["cancelada"] == 1:
            raise ValueError("Esta venda já está cancelada.")
        
        # Busca os itens para devolver ao estoque
        cursor.execute(
            "SELECT produto_id, quantidade FROM itens_venda WHERE venda_id = ?",
            (venda_id,)
        )
        itens = cursor.fetchall()
        
        # Devolve cada item ao estoque
        for item in itens:
            cursor.execute("""
                UPDATE produtos
                SET estoque = estoque + ?
                WHERE id = ?
            """, (item["quantidade"], item["produto_id"]))
        
        # Marca a venda como cancelada
        cursor.execute(
            "UPDATE vendas SET cancelada = 1 WHERE id = ?",
            (venda_id,)
        )
        
        conexao.commit()
        
    except Exception as e:
        conexao.rollback()
        raise e
        
    finally:
        conexao.close()


def obter_total_vendas_periodo(data_inicial, data_final):
    """
    Calcula o total de vendas em um período.
    
    Args:
        data_inicial: Data inicial no formato "YYYY-MM-DD"
        data_final: Data final no formato "YYYY-MM-DD"
        
    Returns:
        Valor total vendido no período (float)
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) as total_vendas
        FROM vendas
        WHERE cancelada = 0
        AND date(data) >= ?
        AND date(data) <= ?
    """, (data_inicial, data_final))
    
    resultado = cursor.fetchone()
    conexao.close()
    
    return resultado["total_vendas"]