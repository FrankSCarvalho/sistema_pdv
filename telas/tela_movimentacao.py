import tkinter as tk
from tkinter import ttk, messagebox

from dao.produtos_dao import listar_produtos
from dao.estoque_dao import (
    registrar_entrada,
    registrar_saida,
    listar_movimentacoes
)


class TelaMovimentacao(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Movimentação de Estoque")
        self.geometry("900x500")

        self.produtos = []
        self.produto_selecionado_id = None

        self._criar_widgets()
        self._carregar_produtos()
        self._carregar_movimentacoes()

    # =========================
    # INTERFACE
    # =========================
    def _criar_widgets(self):
        frame_topo = tk.Frame(self)
        frame_topo.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_topo, text="Produto").grid(row=0, column=0)
        tk.Label(frame_topo, text="Tipo").grid(row=0, column=2)
        tk.Label(frame_topo, text="Quantidade").grid(row=0, column=4)
        tk.Label(frame_topo, text="Observação").grid(row=1, column=0)

        self.combo_produto = ttk.Combobox(frame_topo, width=40, state="readonly")
        self.combo_tipo = ttk.Combobox(
            frame_topo, values=["ENTRADA", "SAIDA"], width=15, state="readonly"
        )
        self.combo_tipo.current(0)

        self.entry_quantidade = tk.Entry(frame_topo, width=10)
        self.entry_observacao = tk.Entry(frame_topo, width=50)

        self.combo_produto.grid(row=0, column=1, padx=5)
        self.combo_tipo.grid(row=0, column=3, padx=5)
        self.entry_quantidade.grid(row=0, column=5, padx=5)
        self.entry_observacao.grid(row=1, column=1, columnspan=5, padx=5, sticky="we")

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_botoes, text="Registrar", command=self._registrar).pack(side="left")
        tk.Button(frame_botoes, text="Limpar", command=self._limpar).pack(side="left", padx=5)

        frame_lista = tk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("id", "produto", "tipo", "quantidade", "data", "observacao")

        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=140)

        self.tree.pack(fill="both", expand=True)

    # =========================
    # AÇÕES
    # =========================
    def _carregar_produtos(self):
        self.produtos = listar_produtos()
        nomes = [
            f"{p.id} - {p.nome} ({p.tamanho or ''} {p.cor or ''})"
            for p in self.produtos
        ]
        self.combo_produto["values"] = nomes

    def _registrar(self):
        if not self.combo_produto.get():
            messagebox.showwarning("Atenção", "Selecione um produto.")
            return

        try:
            quantidade = int(self.entry_quantidade.get())
            if quantidade <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        indice = self.combo_produto.current()
        produto = self.produtos[indice]
        tipo = self.combo_tipo.get()
        observacao = self.entry_observacao.get()

        try:
            if tipo == "ENTRADA":
                registrar_entrada(produto.id, quantidade, observacao)
            else:
                registrar_saida(produto.id, quantidade, observacao)

            messagebox.showinfo("Sucesso", "Movimentação registrada!")
            self._carregar_movimentacoes()
            self._limpar()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _limpar(self):
        self.combo_produto.set("")
        self.combo_tipo.current(0)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_observacao.delete(0, tk.END)

    def _carregar_movimentacoes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        movimentacoes = listar_movimentacoes()

        for mov in movimentacoes:
            self.tree.insert("", tk.END, values=(
                mov["id"],
                f"{mov['nome']} ({mov['tamanho'] or ''} {mov['cor'] or ''})",
                mov["tipo"],
                mov["quantidade"],
                mov["data"],
                mov["observacao"]
            ))
