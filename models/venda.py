class Venda:
    """
    Representa uma venda no sistema.
    
    Atributos:
        id: Identificador único da venda
        data: Data e hora da venda (formato: "YYYY-MM-DD HH:MM:SS")
        total: Valor total da venda
        desconto: Valor do desconto aplicado
        forma_pagamento: Como o cliente pagou (DINHEIRO, PIX, CARTAO_DEBITO, CARTAO_CREDITO)
        observacao: Observações opcionais sobre a venda
        cliente_id: ID do cliente que fez a compra (NULL se não informado)
        usuario_id: ID do vendedor (NULL por enquanto)
        cancelada: 0 = venda ativa, 1 = venda cancelada
        itens: Lista de ItemVenda (produtos vendidos)
    """
    def __init__(
        self,
        id=None,
        data=None,
        total=0.0,
        desconto=0.0,
        forma_pagamento="DINHEIRO",
        observacao=None,
        cliente_id=None,
        usuario_id=None,
        cancelada=0,
        itens=None
    ):
        self.id = id
        self.data = data
        self.total = total
        self.desconto = desconto
        self.forma_pagamento = forma_pagamento
        self.observacao = observacao
        self.cliente_id = cliente_id
        self.usuario_id = usuario_id
        self.cancelada = cancelada
        self.itens = itens or []  # Lista de ItemVenda

    def __repr__(self):
        return (
            f"Venda(id={self.id}, data='{self.data}', "
            f"total=R$ {self.total:.2f}, itens={len(self.itens)})"
        )


class ItemVenda:
    """
    Representa um produto dentro de uma venda.
    
    Atributos:
        id: Identificador único do item
        venda_id: ID da venda que este item pertence
        produto_id: ID do produto vendido
        quantidade: Quantidade vendida
        preco_unitario: Preço do produto no momento da venda
        subtotal: Quantidade × Preço unitário
        produto_nome: Nome do produto (para exibição, não salvo no banco)
    """
    def __init__(
        self,
        id=None,
        venda_id=None,
        produto_id=None,
        quantidade=1,
        preco_unitario=0.0,
        subtotal=0.0,
        produto_nome=None  # Não salvo no banco, apenas para exibir
    ):
        self.id = id
        self.venda_id = venda_id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.subtotal = subtotal
        self.produto_nome = produto_nome

    def calcular_subtotal(self):
        """Calcula o subtotal do item (quantidade × preço unitário)"""
        self.subtotal = self.quantidade * self.preco_unitario
        return self.subtotal

    def __repr__(self):
        return (
            f"ItemVenda(produto_id={self.produto_id}, "
            f"qtd={self.quantidade}, "
            f"subtotal=R$ {self.subtotal:.2f})"
        )