import tkinter as tk
from tkinter import ttk, messagebox

from modelos.produto import Produto
from dao.produtos_dao import (
    inserir_produto,
    atualizar_produto,
    listar_produtos,
    buscar_produto_por_id,
    desativar_produto,
    reativar_produto  
)
from utils.validadores import normalizar_numero, formatar_moeda


class TelaProdutos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Produtos")
        self.geometry("1000x600")  # Aumentei a altura para caber os controles de paginação

        self.produto_selecionado_id = None
        self.produto_selecionado_ativo = True
        
        # ===== NOVO: Variáveis para controlar a paginação =====
        self.pagina_atual = 1  # Começamos na página 1
        self.itens_por_pagina = 16  # Quantos produtos mostrar por página
        self.total_produtos = 0  # Quantos produtos existem no total
        self.produtos_carregados = []  # Lista temporária com TODOS os produtos

        self._criar_widgets()
        self._carregar_produtos()

    # =========================
    # INTERFACE
    # =========================
    def _criar_widgets(self):
        frame_form = tk.Frame(self)
        frame_form.pack(fill="x", padx=10, pady=5)

        # Campos
        tk.Label(frame_form, text="Código de Barras").grid(row=0, column=0)
        tk.Label(frame_form, text="Nome").grid(row=0, column=2)
        tk.Label(frame_form, text="Categoria").grid(row=1, column=0)
        tk.Label(frame_form, text="Tamanho").grid(row=1, column=2)
        tk.Label(frame_form, text="Cor").grid(row=2, column=0)
        tk.Label(frame_form, text="Preço Custo").grid(row=2, column=2)
        tk.Label(frame_form, text="Preço Venda").grid(row=3, column=0)
        tk.Label(frame_form, text="Estoque").grid(row=3, column=2)

        self.entry_codigo = tk.Entry(frame_form, width=25)
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_categoria = tk.Entry(frame_form, width=25)
        self.entry_tamanho = tk.Entry(frame_form, width=10)
        self.entry_cor = tk.Entry(frame_form, width=15)
        self.entry_preco_custo = tk.Entry(frame_form, width=10)
        self.entry_preco_venda = tk.Entry(frame_form, width=10)
        self.entry_estoque = tk.Entry(frame_form, width=10)

        self.entry_codigo.grid(row=0, column=1, padx=5)
        self.entry_nome.grid(row=0, column=3, padx=5)
        self.entry_categoria.grid(row=1, column=1, padx=5)
        self.entry_tamanho.grid(row=1, column=3, padx=5)
        self.entry_cor.grid(row=2, column=1, padx=5)
        self.entry_preco_custo.grid(row=2, column=3, padx=5)
        self.entry_preco_venda.grid(row=3, column=1, padx=5)
        self.entry_estoque.grid(row=3, column=3, padx=5)

        # Botões
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=10, pady=5)

        self.btn_salvar = tk.Button(frame_botoes, text="Salvar", command=self._salvar)
        self.btn_salvar.pack(side="left")
        
        self.btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=self._atualizar)
        self.btn_atualizar.pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="Limpar", command=self._limpar).pack(side="left", padx=5)
        
        self.btn_desativar = tk.Button(
            frame_botoes, 
            text="Desativar", 
            command=self._desativar,
            bg="#ffcccc"
        )
        self.btn_desativar.pack(side="left", padx=5)
        
        self.btn_reativar = tk.Button(
            frame_botoes, 
            text="Reativar", 
            command=self._reativar,
            bg="#ccffcc"
        )
        self.btn_reativar.pack(side="left", padx=5)

        # Checkbox para mostrar inativos
        frame_filtro = tk.Frame(self)
        frame_filtro.pack(fill="x", padx=10, pady=5)
        
        self.var_mostrar_inativos = tk.BooleanVar(value=False)
        self.check_mostrar_inativos = tk.Checkbutton(
            frame_filtro,
            text="Mostrar produtos inativos",
            variable=self.var_mostrar_inativos,
            command=self._carregar_produtos
        )
        self.check_mostrar_inativos.pack(side="left")

        # Tabela
        frame_lista = tk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("id", "status", "nome", "categoria", "tamanho", "cor", "estoque", "preco_custo", "preco_venda", "total_custo", "total_venda")

        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")

        titulos = {
            "id": "ID",
            "status": "Status",
            "nome": "Produto",
            "categoria": "Categoria",
            "tamanho": "Tam.",
            "cor": "Cor",
            "estoque": "Estoque",
            "preco_custo": "Preço Custo",
            "preco_venda": "Preço Venda",
            "total_custo": "Total Custo",
            "total_venda": "Total Venda"
        }

        larguras = {
            "id": 30,
            "status": 70,
            "nome": 180,
            "categoria": 110,
            "tamanho": 60,
            "cor": 60,
            "estoque": 70,
            "preco_custo": 100,
            "preco_venda": 100,
            "total_custo": 100,
            "total_venda": 100
        }

        alinhamento = {
            "id": "center",
            "status": "center",
            "nome": "w",
            "categoria": "w",
            "tamanho": "center",
            "cor": "w",
            "estoque": "center",
            "preco_custo": "e",
            "preco_venda": "e",
            "total_custo": "e",
            "total_venda": "e"
        }

        for col in colunas:
            self.tree.heading(col, text=titulos[col])
            self.tree.column(col, width=larguras[col], anchor=alinhamento[col], stretch=False)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_produto)
        
        # ===== NOVO: Frame para controles de paginação =====
        frame_paginacao = tk.Frame(self)
        frame_paginacao.pack(fill="x", padx=10, pady=5)
        
        # Botão para ir para a primeira página
        self.btn_primeira = tk.Button(
            frame_paginacao, 
            text="<<", 
            command=self._ir_primeira_pagina,
            width=3
        )
        self.btn_primeira.pack(side="left", padx=2)
        
        # Botão página anterior
        self.btn_anterior = tk.Button(
            frame_paginacao, 
            text="<", 
            command=self._pagina_anterior,
            width=3
        )
        self.btn_anterior.pack(side="left", padx=2)
        
        # Label mostrando a página atual
        self.label_pagina = tk.Label(
            frame_paginacao, 
            text="Página 1 de 1",
            font=("Arial", 10)
        )
        self.label_pagina.pack(side="left", padx=10)
        
        # Botão próxima página
        self.btn_proxima = tk.Button(
            frame_paginacao, 
            text=">", 
            command=self._proxima_pagina,
            width=3
        )
        self.btn_proxima.pack(side="left", padx=2)
        
        # Botão para ir para a última página
        self.btn_ultima = tk.Button(
            frame_paginacao, 
            text=">>", 
            command=self._ir_ultima_pagina,
            width=3
        )
        self.btn_ultima.pack(side="left", padx=2)
        
        # Label mostrando total de produtos
        self.label_total = tk.Label(
            frame_paginacao,
            text="Total: 0 produtos",
            font=("Arial", 9)
        )
        self.label_total.pack(side="right", padx=10)
        
        self._atualizar_visibilidade_botoes()

    # =========================
    # AÇÕES
    # =========================
    def _salvar(self):
        try:
            produto = Produto(
                codigo_barras=self.entry_codigo.get() or None,
                nome=self.entry_nome.get(),
                categoria=self.entry_categoria.get(),
                tamanho=self.entry_tamanho.get(),
                cor=self.entry_cor.get(),
                preco_custo=normalizar_numero(self.entry_preco_custo.get()),
                preco_venda=normalizar_numero(self.entry_preco_venda.get()),
                estoque=int(self.entry_estoque.get() or 0)
            )

            inserir_produto(produto)
            self._carregar_produtos()
            self._limpar()

            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!", parent=self)

        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)

    def _atualizar(self):
        if not self.produto_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um produto.", parent=self)
            return

        try:
            produto = Produto(
                id=self.produto_selecionado_id,
                codigo_barras=self.entry_codigo.get() or None,
                nome=self.entry_nome.get(),
                categoria=self.entry_categoria.get(),
                tamanho=self.entry_tamanho.get(),
                cor=self.entry_cor.get(),
                preco_custo=normalizar_numero(self.entry_preco_custo.get()),
                preco_venda=normalizar_numero(self.entry_preco_venda.get()),
                estoque=int(self.entry_estoque.get() or 0),
                ativo=1
            )

            atualizar_produto(produto)
            self._carregar_produtos()
            self._limpar()

            messagebox.showinfo("Sucesso", "Produto atualizado!", parent=self)

        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)

    def _desativar(self):
        if not self.produto_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um produto.", parent=self)
            return

        if messagebox.askyesno("Confirmar", "Deseja desativar este produto?", parent=self):
            desativar_produto(self.produto_selecionado_id)
            self._carregar_produtos()
            self._limpar()
            messagebox.showinfo("Sucesso", "Produto desativado!", parent=self)

    def _reativar(self):
        if not self.produto_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um produto.", parent=self)
            return

        if messagebox.askyesno("Confirmar", "Deseja reativar este produto?", parent=self):
            reativar_produto(self.produto_selecionado_id)
            self._carregar_produtos()
            self._limpar()
            messagebox.showinfo("Sucesso", "Produto reativado!", parent=self)

    def _limpar(self):
        self.produto_selecionado_id = None
        self.produto_selecionado_ativo = True

        self.btn_salvar.config(state="normal")
        self._atualizar_visibilidade_botoes()

        for entry in [
            self.entry_codigo,
            self.entry_nome,
            self.entry_categoria,
            self.entry_tamanho,
            self.entry_cor,
            self.entry_preco_custo,
            self.entry_preco_venda,
            self.entry_estoque
        ]:
            entry.delete(0, tk.END)

    # ===== MODIFICADO: Função principal de carregamento =====
    def _carregar_produtos(self):
        """
        Carrega TODOS os produtos do banco e depois exibe apenas
        os da página atual.
        """
        # 1. Busca TODOS os produtos do banco de dados
        mostrar_inativos = self.var_mostrar_inativos.get()
        self.produtos_carregados = listar_produtos(ativos_apenas=not mostrar_inativos)
        
        # 2. Atualiza o total de produtos
        self.total_produtos = len(self.produtos_carregados)
        
        # 3. Volta para a página 1 quando recarregar
        self.pagina_atual = 1
        
        # 4. Atualiza a exibição da tabela com a página atual
        self._atualizar_tabela()
        
        # 5. Atualiza os controles de paginação
        self._atualizar_controles_paginacao()

    # ===== NOVA FUNÇÃO: Atualiza apenas a tabela =====
    def _atualizar_tabela(self):
        """
        Atualiza a tabela mostrando apenas os produtos da página atual.
        """
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calcula quais produtos mostrar
        # Por exemplo: Se estamos na página 2 e mostramos 20 por página:
        # inicio = (2-1) * 20 = 20 (começa no produto 20)
        # fim = 2 * 20 = 40 (termina no produto 40)
        inicio = (self.pagina_atual - 1) * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        
        # Pega apenas os produtos desta página
        produtos_pagina = self.produtos_carregados[inicio:fim]
        
        # Adiciona os produtos na tabela
        for produto in produtos_pagina:
            total_custo = produto.estoque * (produto.preco_custo or 0)
            total_venda = produto.estoque * (produto.preco_venda or 0)
            
            status = "ATIVO" if produto.ativo == 1 else "INATIVO"

            self.tree.insert("", tk.END, values=(
                produto.id,
                status,
                produto.nome,
                produto.categoria,
                produto.tamanho,
                produto.cor,
                produto.estoque,
                formatar_moeda(produto.preco_custo or 0),
                formatar_moeda(produto.preco_venda),
                formatar_moeda(total_custo),
                formatar_moeda(total_venda)
            ), tags=("inativo",) if produto.ativo == 0 else ())

        self.tree.tag_configure("inativo", background="#ffcccc")

    # ===== NOVA FUNÇÃO: Atualiza os controles de paginação =====
    def _atualizar_controles_paginacao(self):
        """
        Atualiza os botões e labels da paginação.
        """
        # Calcula o número total de páginas
        # Por exemplo: 45 produtos / 20 por página = 2.25 → 3 páginas
        import math
        total_paginas = math.ceil(self.total_produtos / self.itens_por_pagina) if self.total_produtos > 0 else 1
        
        # Atualiza o texto da página
        self.label_pagina.config(text=f"Página {self.pagina_atual} de {total_paginas}")
        self.label_total.config(text=f"Total: {self.total_produtos} produtos")
        
        # Habilita/desabilita botões conforme necessário
        # Desabilita botão "anterior" se estiver na primeira página
        if self.pagina_atual <= 1:
            self.btn_anterior.config(state="disabled")
            self.btn_primeira.config(state="disabled")
        else:
            self.btn_anterior.config(state="normal")
            self.btn_primeira.config(state="normal")
        
        # Desabilita botão "próxima" se estiver na última página
        if self.pagina_atual >= total_paginas:
            self.btn_proxima.config(state="disabled")
            self.btn_ultima.config(state="disabled")
        else:
            self.btn_proxima.config(state="normal")
            self.btn_ultima.config(state="normal")

    # ===== NOVAS FUNÇÕES: Navegação entre páginas =====
    def _proxima_pagina(self):
        """
        Vai para a próxima página.
        """
        import math
        total_paginas = math.ceil(self.total_produtos / self.itens_por_pagina)
        
        if self.pagina_atual < total_paginas:
            self.pagina_atual += 1
            self._atualizar_tabela()
            self._atualizar_controles_paginacao()

    def _pagina_anterior(self):
        """
        Volta para a página anterior.
        """
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self._atualizar_tabela()
            self._atualizar_controles_paginacao()

    def _ir_primeira_pagina(self):
        """
        Vai para a primeira página.
        """
        self.pagina_atual = 1
        self._atualizar_tabela()
        self._atualizar_controles_paginacao()

    def _ir_ultima_pagina(self):
        """
        Vai para a última página.
        """
        import math
        total_paginas = math.ceil(self.total_produtos / self.itens_por_pagina)
        self.pagina_atual = total_paginas
        self._atualizar_tabela()
        self._atualizar_controles_paginacao()

    def _selecionar_produto(self, event):
        item = self.tree.selection()
        if not item:
            return

        valores = self.tree.item(item)["values"]
        produto_id = valores[0]

        produto = buscar_produto_por_id(produto_id)
        if not produto:
            return

        self.produto_selecionado_id = produto.id
        self.produto_selecionado_ativo = (produto.ativo == 1)

        self.btn_salvar.config(state="disabled")
        self._atualizar_visibilidade_botoes()

        self.entry_codigo.delete(0, tk.END)
        if produto.codigo_barras:
            self.entry_codigo.insert(0, produto.codigo_barras)

        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, produto.nome)

        self.entry_categoria.delete(0, tk.END)
        self.entry_categoria.insert(0, produto.categoria or "")

        self.entry_tamanho.delete(0, tk.END)
        self.entry_tamanho.insert(0, produto.tamanho or "")

        self.entry_cor.delete(0, tk.END)
        self.entry_cor.insert(0, produto.cor or "")

        self.entry_preco_custo.delete(0, tk.END)
        self.entry_preco_custo.insert(0, produto.preco_custo or 0)

        self.entry_preco_venda.delete(0, tk.END)
        self.entry_preco_venda.insert(0, produto.preco_venda)

        self.entry_estoque.delete(0, tk.END)
        self.entry_estoque.insert(0, produto.estoque)

    def _atualizar_visibilidade_botoes(self):
        if self.produto_selecionado_id is None:
            self.btn_desativar.pack_forget()
            self.btn_reativar.pack_forget()
        elif self.produto_selecionado_ativo:
            self.btn_desativar.pack(side="left", padx=5)
            self.btn_reativar.pack_forget()
        else:
            self.btn_desativar.pack_forget()
            self.btn_reativar.pack(side="left", padx=5)