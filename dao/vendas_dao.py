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


def obter_vendas_hoje():
    """
    Retorna o total de vendas realizadas hoje.
    
    Returns:
        float: Valor total vendido hoje
    """
    from datetime import date
    
    hoje = date.today().strftime("%Y-%m-%d")
    return obter_total_vendas_periodo(hoje, hoje)


def obter_vendas_mes_atual():
    """
    Retorna o total de vendas do mês atual.
    
    Returns:
        float: Valor total vendido no mês
    """
    from datetime import date
    
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1).strftime("%Y-%m-%d")
    ultimo_dia = hoje.strftime("%Y-%m-%d")
    
    return obter_total_vendas_periodo(primeiro_dia, ultimo_dia)


def obter_vendas_por_forma_pagamento():
    """
    Retorna o total vendido agrupado por forma de pagamento.
    
    Returns:
        List[dict]: Lista com forma_pagamento e total
    """
    from banco.conexao import conectar
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT 
            forma_pagamento,
            COUNT(*) as quantidade,
            SUM(total) as total
        FROM vendas
        WHERE cancelada = 0
        GROUP BY forma_pagamento
        ORDER BY total DESC
    """)
    
    resultados = cursor.fetchall()
    conexao.close()
    
    vendas = []
    for row in resultados:
        vendas.append({
            "forma_pagamento": row["forma_pagamento"],
            "quantidade": row["quantidade"],
            "total": row["total"]
        })
    
    return vendas


def obter_produtos_mais_vendidos(limite=5):
    """
    Retorna os produtos mais vendidos.
    
    Args:
        limite: Número máximo de produtos a retornar
        
    Returns:
        List[dict]: Lista com nome do produto e quantidade vendida
    """
    from banco.conexao import conectar
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT 
            p.nome,
            p.tamanho,
            p.cor,
            SUM(iv.quantidade) as total_vendido,
            SUM(iv.subtotal) as valor_total
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        JOIN vendas v ON v.id = iv.venda_id
        WHERE v.cancelada = 0
        GROUP BY iv.produto_id
        ORDER BY total_vendido DESC
        LIMIT ?
    """, (limite,))
    
    resultados = cursor.fetchall()
    conexao.close()
    
    produtos = []
    for row in resultados:
        nome_completo = f"{row['nome']}"
        if row['tamanho']:
            nome_completo += f" ({row['tamanho']}"
            if row['cor']:
                nome_completo += f" {row['cor']}"
            nome_completo += ")"
        elif row['cor']:
            nome_completo += f" ({row['cor']})"
        
        produtos.append({
            "nome": nome_completo,
            "quantidade": row["total_vendido"],
            "valor_total": row["valor_total"]
        })
    
    return produtos


def obter_vendas_ultimos_dias(dias=7):
    """
    Retorna o total de vendas dos últimos N dias.
    
    Args:
        dias: Número de dias a buscar
        
    Returns:
        List[dict]: Lista com data e total vendido
    """
    from banco.conexao import conectar
    from datetime import date, timedelta
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Calcula as datas
    hoje = date.today()
    data_inicial = (hoje - timedelta(days=dias-1)).strftime("%Y-%m-%d")
    data_final = hoje.strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT 
            DATE(data) as data,
            COUNT(*) as quantidade,
            SUM(total) as total
        FROM vendas
        WHERE cancelada = 0
        AND DATE(data) BETWEEN ? AND ?
        GROUP BY DATE(data)
        ORDER BY data ASC
    """, (data_inicial, data_final))
    
    resultados = cursor.fetchall()
    conexao.close()
    
    # Cria dicionário com todas as datas (incluindo dias sem vendas)
    vendas_por_dia = {}
    data_atual = hoje - timedelta(days=dias-1)
    while data_atual <= hoje:
        vendas_por_dia[data_atual.strftime("%Y-%m-%d")] = 0.0
        data_atual += timedelta(days=1)
    
    # Preenche com os dados reais
    for row in resultados:
        vendas_por_dia[row["data"]] = row["total"]
    
    # Converte para lista
    vendas = []
    for data_str, total in sorted(vendas_por_dia.items()):
        # Formata data para exibição (DD/MM)
        data_obj = date.fromisoformat(data_str)
        data_formatada = data_obj.strftime("%d/%m")
        
        vendas.append({
            "data": data_formatada,
            "total": total
        })
    
    return vendas


def obter_estatisticas_gerais():
    """
    Retorna estatísticas gerais do sistema.
    
    Returns:
        dict: Dicionário com várias estatísticas
    """
    from banco.conexao import conectar
    from dao.clientes_dao import obter_total_clientes_ativos
    from dao.produtos_dao import listar_produtos
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Total de vendas (todas)
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM vendas
        WHERE cancelada = 0
    """)
    total_vendas = cursor.fetchone()["total"]
    
    # Total de produtos vendidos (quantidade)
    cursor.execute("""
        SELECT SUM(iv.quantidade) as total
        FROM itens_venda iv
        JOIN vendas v ON v.id = iv.venda_id
        WHERE v.cancelada = 0
    """)
    total_produtos_vendidos = cursor.fetchone()["total"] or 0
    
    # Ticket médio
    cursor.execute("""
        SELECT AVG(total) as media
        FROM vendas
        WHERE cancelada = 0
        AND total > 0
    """)
    ticket_medio = cursor.fetchone()["media"] or 0.0
    
    conexao.close()
    
    # Total de clientes ativos
    total_clientes = obter_total_clientes_ativos()
    
    # Total de produtos cadastrados
    produtos = listar_produtos(ativos_apenas=True)
    total_produtos = len(produtos)
    
    # Total em estoque (valor)
    valor_estoque = sum(
        (p.preco_venda or 0) * p.estoque 
        for p in produtos
    )
    
    return {
        "total_vendas": total_vendas,
        "total_clientes": total_clientes,
        "total_produtos": total_produtos,
        "total_produtos_vendidos": total_produtos_vendidos,
        "ticket_medio": ticket_medio,
        "valor_estoque": valor_estoque
    }