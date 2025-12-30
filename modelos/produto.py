class Produto:
    def __init__(
            self,
            id=None,
            codigo_barras=None,
            nome=None,
            categoria=None,
            tamanho=None,
            cor=None,
            preco_custo=None,
            preco_venda=None,
            estoque=0,
            ativo=1
    ):
        self.id = id
        self.codigo_barras = codigo_barras
        self.nome = nome
        self.categoria = categoria
        self.tamanho = tamanho
        self.cor = cor
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.estoque = estoque
        self.ativo = ativo

    def __repr__(self):
        return (
            f"Produto(id={self.id}, nome='{self.nome}', "
            f"tamanho='{self.tamanho}', cor='{self.cor}', "
            f"estoque={self.estoque})"
        )