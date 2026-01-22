import tkinter as tk
from tkinter import ttk, messagebox

from dao.produtos_dao import listar_produtos
from dao.estoque_dao import (
    registrar_entrada,
    registrar_saida,
    listar_movimentacoes
)


class TelaMovimentacao(tk.Toplevel):
    def __init__(self, master=None, usuario_logado=None):
        super().__init__(master)
        self.title("Movimentação de Estoque")
        self.geometry("1000x600")
        
        # Configura cor de fundo
        self.configure(bg="#f5f5f5")

        self.produtos = []
        self.produto_selecionado_id = None

        self._criar_widgets()
        self._carregar_produtos()
        self._carregar_movimentacoes()

    # =========================
    # INTERFACE
    # =========================
    def _criar_widgets(self):
        # ========================================
        # FRAME SUPERIOR - Cabeçalho
        # ========================================
        frame_header = tk.Frame(self, bg="#2196F3", height=60)
        frame_header.pack(fill="x", side="top")
        frame_header.pack_propagate(False)
        
        tk.Label(
            frame_header,
            text="📊 Movimentação de Estoque",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=15)
        
        # ========================================
        # FRAME FORMULÁRIO - Registro de Movimentação
        # ========================================
        frame_form = tk.LabelFrame(
            self,
            text="  📝 Registrar Movimentação  ",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=15,
            bg="white",
            fg="#333"
        )
        frame_form.pack(fill="x", padx=15, pady=(15, 10))

        # LINHA 1: Produto e Tipo
        row1 = tk.Frame(frame_form, bg="white")
        row1.pack(fill="x", pady=(0, 10))
        
        # Produto
        tk.Label(
            row1,
            text="Produto:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.combo_produto = ttk.Combobox(
            row1,
            width=45,
            state="readonly",
            font=("Arial", 10)
        )
        self.combo_produto.pack(side="left", padx=(0, 20))
        
        # Tipo
        tk.Label(
            row1,
            text="Tipo:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.combo_tipo = ttk.Combobox(
            row1,
            values=["ENTRADA", "SAIDA"],
            width=15,
            state="readonly",
            font=("Arial", 10)
        )
        self.combo_tipo.current(0)
        self.combo_tipo.pack(side="left")
        
        # Adiciona ícone visual ao tipo
        self.combo_tipo.bind("<<ComboboxSelected>>", self._atualizar_cor_tipo)

        # LINHA 2: Quantidade e Observação
        row2 = tk.Frame(frame_form, bg="white")
        row2.pack(fill="x", pady=(0, 10))
        
        # Quantidade
        tk.Label(
            row2,
            text="Quantidade:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.entry_quantidade = tk.Entry(
            row2,
            width=12,
            font=("Arial", 11),
            relief="solid",
            borderwidth=1
        )
        self.entry_quantidade.pack(side="left", padx=(0, 20))
        
        # Observação
        tk.Label(
            row2,
            text="Observação:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.entry_observacao = tk.Entry(
            row2,
            width=50,
            font=("Arial", 10),
            relief="solid",
            borderwidth=1
        )
        self.entry_observacao.pack(side="left", fill="x", expand=True)

        # LINHA 3: Botões de Ação
        row3 = tk.Frame(frame_form, bg="white")
        row3.pack(fill="x", pady=(5, 0))
        
        self.btn_registrar = tk.Button(
            row3,
            text="✅ Registrar Movimentação",
            command=self._registrar,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.btn_registrar.pack(side="left", padx=(0, 5))
        
        # Efeito hover no botão registrar
        self.btn_registrar.bind("<Enter>", lambda e: self.btn_registrar.config(bg="#45a049"))
        self.btn_registrar.bind("<Leave>", lambda e: self.btn_registrar.config(bg="#4CAF50"))
        
        tk.Button(
            row3,
            text="🗑️ Limpar",
            command=self._limpar,
            bg="#757575",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left")

        # ========================================
        # FRAME HISTÓRICO - Lista de Movimentações
        # ========================================
        frame_lista = tk.LabelFrame(
            self,
            text="  📋 Histórico de Movimentações  ",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10,
            bg="white",
            fg="#333"
        )
        frame_lista.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Container para a Treeview com scrollbar
        tree_container = tk.Frame(frame_lista, bg="white")
        tree_container.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Treeview
        colunas = ("id", "produto", "tipo", "quantidade", "data", "observacao")

        self.tree = ttk.Treeview(
            tree_container,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        
        scrollbar.config(command=self.tree.yview)

        # Configuração das colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("produto", text="Produto")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("observacao", text="Observação")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("produto", width=300, anchor="w")
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("quantidade", width=100, anchor="center")
        self.tree.column("data", width=150, anchor="center")
        self.tree.column("observacao", width=250, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)
        
        # Estilo para linhas alternadas
        self.tree.tag_configure("entrada", background="#e8f5e9")
        self.tree.tag_configure("saida", background="#ffebee")
        
        # Rodapé com informações
        frame_footer = tk.Frame(self, bg="#f5f5f5")
        frame_footer.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(
            frame_footer,
            text="💡 Dica: Selecione ENTRADA para adicionar produtos ou SAIDA para retirar do estoque",
            font=("Arial", 9, "italic"),
            bg="#f5f5f5",
            fg="#666"
        ).pack(side="left")

    # =========================
    # AÇÕES
    # =========================
    def _atualizar_cor_tipo(self, event=None):
        """Atualiza a aparência visual baseado no tipo selecionado."""
        tipo = self.combo_tipo.get()
        
        if tipo == "ENTRADA":
            self.btn_registrar.config(bg="#4CAF50")
        else:
            self.btn_registrar.config(bg="#f44336")

    def _carregar_produtos(self):
        self.produtos = listar_produtos()
        nomes = [
            f"{p.id} - {p.nome} ({p.tamanho or ''} {p.cor or ''}) - Estoque: {p.estoque}"
            for p in self.produtos
        ]
        self.combo_produto["values"] = nomes

    def _registrar(self):
        if not self.combo_produto.get():
            messagebox.showwarning(
                "Atenção",
                "⚠️ Por favor, selecione um produto.",
                parent=self
            )
            self.combo_produto.focus()
            return

        try:
            quantidade = int(self.entry_quantidade.get())
            if quantidade <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Erro",
                "❌ Quantidade inválida.\nDigite um número maior que zero.",
                parent=self
            )
            self.entry_quantidade.focus()
            self.entry_quantidade.select_range(0, tk.END)
            return

        indice = self.combo_produto.current()
        produto = self.produtos[indice]
        tipo = self.combo_tipo.get()
        observacao = self.entry_observacao.get().strip() or None

        try:
            if tipo == "ENTRADA":
                registrar_entrada(produto.id, quantidade, observacao)
                mensagem = f"✅ Entrada registrada com sucesso!\n\n"
                mensagem += f"Produto: {produto.nome}\n"
                mensagem += f"Quantidade: +{quantidade}\n"
                mensagem += f"Novo estoque: {produto.estoque + quantidade}"
            else:
                registrar_saida(produto.id, quantidade, observacao)
                mensagem = f"✅ Saída registrada com sucesso!\n\n"
                mensagem += f"Produto: {produto.nome}\n"
                mensagem += f"Quantidade: -{quantidade}\n"
                mensagem += f"Novo estoque: {produto.estoque - quantidade}"

            messagebox.showinfo("Sucesso", mensagem, parent=self)
            
            # Atualiza a lista e recarrega produtos
            self._carregar_movimentacoes()
            self._carregar_produtos()
            self._limpar()

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"❌ Não foi possível registrar a movimentação:\n\n{str(e)}",
                parent=self
            )

    def _limpar(self):
        """Limpa todos os campos do formulário."""
        self.combo_produto.set("")
        self.combo_tipo.current(0)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_observacao.delete(0, tk.END)
        self.combo_produto.focus()
        self._atualizar_cor_tipo()

    def _carregar_movimentacoes(self):
        """Carrega o histórico de movimentações na tabela."""
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        movimentacoes = listar_movimentacoes()

        # Adiciona as movimentações com cores alternadas
        for mov in movimentacoes:
            produto_info = f"{mov['nome']}"
            if mov['tamanho'] or mov['cor']:
                produto_info += f" ({mov['tamanho'] or ''} {mov['cor'] or ''})"
            
            # Define a tag baseada no tipo
            tag = "entrada" if mov["tipo"] == "ENTRADA" else "saida"
            
            # Formata a data (remove os segundos para ficar mais limpo)
            data_formatada = mov["data"][:16] if mov["data"] else ""
            
            # Adiciona prefixo visual à quantidade
            qtd_display = f"+{mov['quantidade']}" if mov["tipo"] == "ENTRADA" else f"-{mov['quantidade']}"
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    mov["id"],
                    produto_info,
                    f"📥 {mov['tipo']}" if mov["tipo"] == "ENTRADA" else f"📤 {mov['tipo']}",
                    qtd_display,
                    data_formatada,
                    mov["observacao"] or "—"
                ),
                tags=(tag,)
            )