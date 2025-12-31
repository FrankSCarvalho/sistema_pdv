import tkinter as tk
from tkinter import ttk, messagebox

from modelos.produto import Produto
from dao.produtos_dao import (
    inserir_produto,
    atualizar_produto,
    listar_produtos,
    buscar_produto_por_id,
    desativar_produto
)


class TelaProdutos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Produtos")
        self.geometry("900x500")

        self.produto_selecionado_id = None

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

        tk.Button(frame_botoes, text="Salvar", command=self._salvar).pack(side="left")
        tk.Button(frame_botoes, text="Atualizar", command=self._atualizar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Limpar", command=self._limpar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Desativar", command=self._desativar).pack(side="left", padx=5)

        # Tabela
        frame_lista = tk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("id", "nome", "categoria", "tamanho", "cor", "estoque", "preco_venda")

        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_produto)

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
                preco_custo=float(self.entry_preco_custo.get() or 0),
                preco_venda=float(self.entry_preco_venda.get()),
                estoque=int(self.entry_estoque.get() or 0)
            )

            inserir_produto(produto)
            self._carregar_produtos()
            self._limpar()

            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!", parent=self)

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
                preco_custo=float(self.entry_preco_custo.get() or 0),
                preco_venda=float(self.entry_preco_venda.get()),
                estoque=int(self.entry_estoque.get() or 0),
                ativo=1
            )

            atualizar_produto(produto)
            self._carregar_produtos()
            self._limpar()

            messagebox.showinfo("Sucesso", "Produto atualizado!",parent=self)

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

    def _limpar(self):
        self.produto_selecionado_id = None
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

    def _carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for produto in listar_produtos():
            self.tree.insert("", tk.END, values=(
                produto.id,
                produto.nome,
                produto.categoria,
                produto.tamanho,
                produto.cor,
                produto.estoque,
                produto.preco_venda
            ))

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
