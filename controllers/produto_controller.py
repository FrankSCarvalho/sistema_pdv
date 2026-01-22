"""
Controlador de Produtos
Gerencia todas as operações relacionadas a produtos
"""

from database import conectar
from models import Produto


class ProdutoController:
    """
    Controlador responsável por gerenciar produtos.
    
    Este controlador centraliza todas as operações de produtos,
    fazendo a ponte entre a interface (View) e o banco de dados (Model).
    """
    
    @staticmethod
    def criar_produto(produto_data):
        """
        Cria um novo produto no sistema.
        
        Args:
            produto_data (dict): Dicionário com os dados do produto
                Exemplo: {
                    'codigo_barras': '123456',
                    'nome': 'Camiseta',
                    'categoria': 'Roupas',
                    'tamanho': 'M',
                    'cor': 'Azul',
                    'preco_custo': 15.00,
                    'preco_venda': 39.90,
                    'estoque': 50
                }
        
        Returns:
            Produto: Objeto Produto com ID preenchido
        
        Raises:
            ValueError: Se dados obrigatórios estiverem faltando
        """
        # Validações
        if not produto_data.get('nome'):
            raise ValueError("O nome do produto é obrigatório")
        
        if not produto_data.get('preco_venda'):
            raise ValueError("O preço de venda é obrigatório")
        
        # Cria o objeto Produto
        produto = Produto(
            codigo_barras=produto_data.get('codigo_barras'),
            nome=produto_data.get('nome'),
            categoria=produto_data.get('categoria'),
            tamanho=produto_data.get('tamanho'),
            cor=produto_data.get('cor'),
            preco_custo=produto_data.get('preco_custo'),
            preco_venda=produto_data.get('preco_venda'),
            estoque=produto_data.get('estoque', 0),
            ativo=1
        )
        
        # Salva no banco
        conexao = conectar()
        cursor = conexao.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO produtos (
                    codigo_barras, nome, categoria, tamanho, cor,
                    preco_custo, preco_venda, estoque, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            
            return produto
            
        except Exception as e:
            conexao.rollback()
            raise e
        finally:
            conexao.close()
    
    @staticmethod
    def atualizar_produto(produto):
        """
        Atualiza os dados de um produto existente.
        
        Args:
            produto (Produto): Objeto Produto com dados atualizados
        
        Raises:
            ValueError: Se o produto não tiver ID ou não existir
        """
        if not produto.id:
            raise ValueError("O ID do produto é obrigatório para atualização")
        
        conexao = conectar()
        cursor = conexao.cursor()
        
        try:
            cursor.execute("""
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
            """, (
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
            
            if cursor.rowcount == 0:
                raise ValueError(f"Produto com ID {produto.id} não encontrado")
            
            conexao.commit()
            
        except Exception as e:
            conexao.rollback()
            raise e
        finally:
            conexao.close()
    
    @staticmethod
    def buscar_por_id(produto_id):
        """
        Busca um produto pelo ID.
        
        Args:
            produto_id (int): ID do produto
        
        Returns:
            Produto ou None: Objeto Produto se encontrado
        """
        conexao = conectar()
        cursor = conexao.cursor()
        
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        linha = cursor.fetchone()
        conexao.close()
        
        if linha:
            return ProdutoController._linha_para_produto(linha)
        return None
    
    @staticmethod
    def buscar_por_codigo_barras(codigo_barras):
        """
        Busca um produto pelo código de barras.
        
        Args:
            codigo_barras (str): Código de barras do produto
        
        Returns:
            Produto ou None: Objeto Produto se encontrado (apenas ativos)
        """
        conexao = conectar()
        cursor = conexao.cursor()
        
        cursor.execute(
            "SELECT * FROM produtos WHERE codigo_barras = ? AND ativo = 1",
            (codigo_barras,)
        )
        linha = cursor.fetchone()
        conexao.close()
        
        if linha:
            return ProdutoController._linha_para_produto(linha)
        return None
    
    @staticmethod
    def listar_produtos(filtros=None):
        """
        Lista produtos com filtros opcionais.
        
        Args:
            filtros (dict): Dicionário com filtros opcionais
                Exemplo: {
                    'ativos_apenas': True,
                    'nome': 'camiseta',
                    'categoria': 'roupas',
                    'preco_min': 10.0,
                    'preco_max': 100.0,
                    'estoque_baixo': 10,
                    'ordenar_por': 'nome',
                    'ordem_crescente': True
                }
        
        Returns:
            list: Lista de objetos Produto
        """
        if filtros is None:
            filtros = {}
        
        conexao = conectar()
        cursor = conexao.cursor()
        
        # Monta a query dinamicamente
        sql = "SELECT * FROM produtos WHERE 1=1"
        parametros = []
        
        # Aplica filtros
        if filtros.get('ativos_apenas', True):
            sql += " AND ativo = 1"
        
        if filtros.get('nome'):
            sql += " AND nome LIKE ?"
            parametros.append(f"%{filtros['nome']}%")
        
        if filtros.get('categoria'):
            sql += " AND categoria LIKE ?"
            parametros.append(f"%{filtros['categoria']}%")
        
        if filtros.get('codigo_barras'):
            sql += " AND codigo_barras LIKE ?"
            parametros.append(f"%{filtros['codigo_barras']}%")
        
        if filtros.get('tamanho'):
            sql += " AND tamanho LIKE ?"
            parametros.append(f"%{filtros['tamanho']}%")
        
        if filtros.get('cor'):
            sql += " AND cor LIKE ?"
            parametros.append(f"%{filtros['cor']}%")
        
        if filtros.get('preco_min') is not None:
            sql += " AND preco_venda >= ?"
            parametros.append(filtros['preco_min'])
        
        if filtros.get('preco_max') is not None:
            sql += " AND preco_venda <= ?"
            parametros.append(filtros['preco_max'])
        
        if filtros.get('estoque_baixo') is not None:
            sql += " AND estoque <= ?"
            parametros.append(filtros['estoque_baixo'])
        
        # Ordenação
        ordenar_por = filtros.get('ordenar_por', 'nome')
        colunas_validas = ['nome', 'categoria', 'preco_venda', 'estoque', 'tamanho', 'cor']
        if ordenar_por not in colunas_validas:
            ordenar_por = 'nome'
        
        direcao = 'ASC' if filtros.get('ordem_crescente', True) else 'DESC'
        sql += f" ORDER BY {ordenar_por} {direcao}"
        
        # Executa query
        cursor.execute(sql, parametros)
        linhas = cursor.fetchall()
        conexao.close()
        
        # Converte para objetos Produto
        produtos = []
        for linha in linhas:
            produtos.append(ProdutoController._linha_para_produto(linha))
        
        return produtos
    
    @staticmethod
    def desativar_produto(produto_id):
        """
        Desativa um produto (soft delete).
        
        Args:
            produto_id (int): ID do produto a desativar
        """
        conexao = conectar()
        cursor = conexao.cursor()
        
        cursor.execute(
            "UPDATE produtos SET ativo = 0 WHERE id = ?",
            (produto_id,)
        )
        
        conexao.commit()
        conexao.close()
    
    @staticmethod
    def reativar_produto(produto_id):
        """
        Reativa um produto desativado.
        
        Args:
            produto_id (int): ID do produto a reativar
        """
        conexao = conectar()
        cursor = conexao.cursor()
        
        cursor.execute(
            "UPDATE produtos SET ativo = 1 WHERE id = ?",
            (produto_id,)
        )
        
        conexao.commit()
        conexao.close()
    
    @staticmethod
    def _linha_para_produto(linha):
        """
        Converte uma linha do banco em objeto Produto.
        
        Args:
            linha: Row do SQLite
        
        Returns:
            Produto: Objeto Produto preenchido
        """
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