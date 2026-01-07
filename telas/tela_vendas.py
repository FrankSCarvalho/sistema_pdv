import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from modelos.venda import Venda, ItemVenda
from modelos.cliente import Cliente
from dao.vendas_dao import registrar_venda
from dao.produtos_dao import buscar_produto_por_codigo_barras, listar_produtos
from dao.clientes_dao import listar_clientes, inserir_cliente
from utils.validadores import normalizar_numero, formatar_moeda


class TelaVendas(tk.Toplevel):
    """
    Tela principal de vendas (PDV - Ponto de Venda).
    
    Permite:
    - Adicionar produtos ao carrinho
    - Selecionar cliente (opcional)
    - Aplicar desconto
    - Escolher forma de pagamento
    - Finalizar venda
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("🛒 Sistema de Vendas - PDV")
        self.geometry("1100x700")
        
        # Carrinho de compras (lista de ItemVenda)
        self.itens_carrinho = []
        
        # Cliente selecionado (pode ser None)
        self.cliente_selecionado = None
        
        # Listas auxiliares
        self.clientes = []
        self.produtos = []
        
        self._criar_widgets()
        self._carregar_clientes()
        self._carregar_produtos()
        self._atualizar_totais()
        
        # Foca no campo de busca de produto
        self.entry_busca_produto.focus()
    
    # =========================
    # INTERFACE
    # =========================
    
    def _criar_widgets(self):
        """Cria todos os elementos da interface."""
        
        # ========================================
        # FRAME SUPERIOR - Busca de Produtos e Cliente
        # ========================================
        frame_topo = tk.LabelFrame(self, text="📦 Adicionar Produto", padx=10, pady=10)
        frame_topo.pack(fill="x", padx=10, pady=(10, 5))
        
        # Linha 1: Busca de produto
        tk.Label(frame_topo, text="Produto:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        
        self.entry_busca_produto = tk.Entry(frame_topo, width=40, font=("Arial", 10))
        self.entry_busca_produto.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.entry_busca_produto.bind("<Return>", lambda e: self._buscar_produto())
        
        tk.Button(
            frame_topo, 
            text="🔍 Buscar", 
            command=self._buscar_produto,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2"
        ).grid(row=0, column=2, padx=2)
        
        tk.Button(
            frame_topo, 
            text="✖ Limpar", 
            command=self._limpar_busca,
            cursor="hand2"
        ).grid(row=0, column=3, padx=2)
        
        tk.Label(
            frame_topo, 
            text="💡 Digite o código de barras ou nome do produto",
            font=("Arial", 8),
            fg="gray"
        ).grid(row=1, column=1, columnspan=3, sticky="w")
        
        # Linha 2: Seleção de cliente
        tk.Label(frame_topo, text="Cliente:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(10, 5)
        )
        
        self.combo_cliente = ttk.Combobox(
            frame_topo, 
            width=37, 
            state="readonly",
            font=("Arial", 10)
        )
        self.combo_cliente.grid(row=2, column=1, padx=5, pady=(10, 5), sticky="we")
        self.combo_cliente.bind("<<ComboboxSelected>>", self._selecionar_cliente)
        
        tk.Button(
            frame_topo, 
            text="➕ Novo Cliente", 
            command=self._abrir_cadastro_rapido_cliente,
            cursor="hand2"
        ).grid(row=2, column=2, padx=2, pady=(10, 5))
        
        tk.Button(
            frame_topo, 
            text="✖ Remover", 
            command=self._remover_cliente,
            cursor="hand2"
        ).grid(row=2, column=3, padx=2, pady=(10, 5))
        
        frame_topo.columnconfigure(1, weight=1)
        
        # ========================================
        # FRAME CENTRAL - Carrinho de Compras
        # ========================================
        frame_carrinho = tk.LabelFrame(
            self, 
            text="🛒 Carrinho de Compras", 
            padx=10, 
            pady=10
        )
        frame_carrinho.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tabela do carrinho
        colunas = ("produto", "quantidade", "preco_unitario", "subtotal")
        
        self.tree_carrinho = ttk.Treeview(
            frame_carrinho, 
            columns=colunas, 
            show="headings",
            height=12
        )
        
        # Configurar colunas
        self.tree_carrinho.heading("produto", text="Produto")
        self.tree_carrinho.heading("quantidade", text="Quantidade")
        self.tree_carrinho.heading("preco_unitario", text="Preço Unitário")
        self.tree_carrinho.heading("subtotal", text="Subtotal")
        
        self.tree_carrinho.column("produto", width=400, anchor="w")
        self.tree_carrinho.column("quantidade", width=100, anchor="center")
        self.tree_carrinho.column("preco_unitario", width=150, anchor="e")
        self.tree_carrinho.column("subtotal", width=150, anchor="e")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame_carrinho, 
            orient="vertical", 
            command=self.tree_carrinho.yview
        )
        self.tree_carrinho.configure(yscrollcommand=scrollbar.set)
        
        self.tree_carrinho.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de ação no carrinho
        frame_acoes_carrinho = tk.Frame(frame_carrinho)
        frame_acoes_carrinho.pack(fill="x", pady=(10, 0))
        
        tk.Button(
            frame_acoes_carrinho,
            text="➕ Aumentar Qtd",
            command=self._aumentar_quantidade,
            cursor="hand2"
        ).pack(side="left", padx=2)
        
        tk.Button(
            frame_acoes_carrinho,
            text="➖ Diminuir Qtd",
            command=self._diminuir_quantidade,
            cursor="hand2"
        ).pack(side="left", padx=2)
        
        tk.Button(
            frame_acoes_carrinho,
            text="🗑️ Remover Item",
            command=self._remover_item,
            bg="#f44336",
            fg="white",
            cursor="hand2"
        ).pack(side="left", padx=2)
        
        # ========================================
        # FRAME INFERIOR - Totais e Finalização
        # ========================================
        frame_rodape = tk.Frame(self, padx=10, pady=10)
        frame_rodape.pack(fill="x", padx=10, pady=(5, 10))
        
        # Coluna esquerda - Forma de pagamento
        frame_esquerda = tk.Frame(frame_rodape)
        frame_esquerda.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            frame_esquerda, 
            text="Forma de Pagamento:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.combo_pagamento = ttk.Combobox(
            frame_esquerda,
            values=["DINHEIRO", "PIX", "CARTAO_DEBITO", "CARTAO_CREDITO"],
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        self.combo_pagamento.current(0)
        self.combo_pagamento.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        # Coluna direita - Totais
        frame_direita = tk.Frame(frame_rodape)
        frame_direita.pack(side="right")
        
        # Subtotal
        tk.Label(
            frame_direita, 
            text="Subtotal:",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="e", pady=2)
        
        self.label_subtotal = tk.Label(
            frame_direita,
            text="R$ 0,00",
            font=("Arial", 10),
            fg="blue"
        )
        self.label_subtotal.grid(row=0, column=1, sticky="e", pady=2, padx=(10, 0))
        
        # Desconto
        tk.Label(
            frame_direita,
            text="Desconto:",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="e", pady=2)
        
        frame_desconto = tk.Frame(frame_direita)
        frame_desconto.grid(row=1, column=1, sticky="e", pady=2, padx=(10, 0))
        
        self.entry_desconto = tk.Entry(frame_desconto, width=10, font=("Arial", 10))
        self.entry_desconto.insert(0, "0")
        self.entry_desconto.pack(side="left")
        self.entry_desconto.bind("<KeyRelease>", lambda e: self._atualizar_totais())
        
        self.label_desconto_valor = tk.Label(
            frame_desconto,
            text="R$ 0,00",
            font=("Arial", 10),
            fg="red"
        )
        self.label_desconto_valor.pack(side="left", padx=(5, 0))
        
        # Total
        tk.Label(
            frame_direita,
            text="TOTAL:",
            font=("Arial", 14, "bold")
        ).grid(row=2, column=0, sticky="e", pady=(10, 2))
        
        self.label_total = tk.Label(
            frame_direita,
            text="R$ 0,00",
            font=("Arial", 16, "bold"),
            fg="green"
        )
        self.label_total.grid(row=2, column=1, sticky="e", pady=(10, 2), padx=(10, 0))
        
        # Botões finais
        frame_botoes = tk.Frame(self, padx=10, pady=5)
        frame_botoes.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(
            frame_botoes,
            text="✅ FINALIZAR VENDA",
            command=self._finalizar_venda,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(
            frame_botoes,
            text="🗑️ CANCELAR/LIMPAR",
            command=self._limpar_carrinho,
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    # =========================
    # CARREGAMENTO DE DADOS
    # =========================
    
    def _carregar_clientes(self):
        """Carrega a lista de clientes no combobox."""
        self.clientes = listar_clientes(ativos_apenas=True)
        
        nomes = ["-- Nenhum cliente selecionado --"] + [
            f"{c.id} - {c.nome}" + (f" ({c.telefone})" if c.telefone else "")
            for c in self.clientes
        ]
        
        self.combo_cliente["values"] = nomes
        self.combo_cliente.current(0)
    
    def _carregar_produtos(self):
        """Carrega lista de produtos para busca."""
        self.produtos = listar_produtos(ativos_apenas=True)
    
    # =========================
    # BUSCA E ADIÇÃO DE PRODUTOS
    # =========================
    
    def _buscar_produto(self):
        """
        Busca um produto por código de barras ou nome.
        Se encontrar apenas 1, adiciona automaticamente ao carrinho.
        Se encontrar vários, mostra uma janela para escolher.
        """
        busca = self.entry_busca_produto.get().strip()
        
        if not busca:
            messagebox.showwarning("Atenção", "Digite um código ou nome do produto.", parent=self)
            return
        
        # Tenta buscar por código de barras primeiro
        produto = buscar_produto_por_codigo_barras(busca)
        
        if produto:
            self._adicionar_ao_carrinho(produto)
            return
        
        # Se não encontrou por código, busca por nome
        produtos_encontrados = [
            p for p in self.produtos 
            if busca.lower() in p.nome.lower()
        ]
        
        if not produtos_encontrados:
            messagebox.showwarning(
                "Produto não encontrado",
                f"Nenhum produto encontrado com '{busca}'.",
                parent=self
            )
            return
        
        if len(produtos_encontrados) == 1:
            # Apenas 1 produto, adiciona direto
            self._adicionar_ao_carrinho(produtos_encontrados[0])
        else:
            # Vários produtos, mostra janela de seleção
            self._mostrar_selecao_produtos(produtos_encontrados)
    
    def _mostrar_selecao_produtos(self, produtos):
        """Mostra janela para selecionar qual produto adicionar."""
        janela = tk.Toplevel(self)
        janela.title("Selecione o Produto")
        janela.geometry("600x400")
        janela.transient(self)
        janela.grab_set()
        
        tk.Label(
            janela,
            text=f"Encontrados {len(produtos)} produtos. Selecione um:",
            font=("Arial", 11, "bold")
        ).pack(pady=10)
        
        # Lista de produtos
        frame_lista = tk.Frame(janela)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        colunas = ("nome", "tamanho", "cor", "estoque", "preco")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        tree.heading("nome", text="Nome")
        tree.heading("tamanho", text="Tamanho")
        tree.heading("cor", text="Cor")
        tree.heading("estoque", text="Estoque")
        tree.heading("preco", text="Preço")
        
        tree.column("nome", width=250)
        tree.column("tamanho", width=80, anchor="center")
        tree.column("cor", width=80)
        tree.column("estoque", width=80, anchor="center")
        tree.column("preco", width=100, anchor="e")
        
        for p in produtos:
            tree.insert("", tk.END, values=(
                p.nome,
                p.tamanho or "",
                p.cor or "",
                p.estoque,
                formatar_moeda(p.preco_venda)
            ), tags=(p.id,))
        
        tree.pack(fill="both", expand=True)
        
        def adicionar_selecionado():
            selecao = tree.selection()
            if not selecao:
                messagebox.showwarning("Atenção", "Selecione um produto.", parent=janela)
                return
            
            produto_id = int(tree.item(selecao[0])["tags"][0])
            produto = next(p for p in produtos if p.id == produto_id)
            
            self._adicionar_ao_carrinho(produto)
            janela.destroy()
        
        # Botões
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(fill="x", padx=10, pady=10)
        
        tk.Button(
            frame_botoes,
            text="✅ Adicionar",
            command=adicionar_selecionado,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(
            frame_botoes,
            text="❌ Cancelar",
            command=janela.destroy,
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        tree.bind("<Double-1>", lambda e: adicionar_selecionado())
    
    def _adicionar_ao_carrinho(self, produto):
        """Adiciona um produto ao carrinho."""
        if produto.estoque <= 0:
            messagebox.showwarning(
                "Estoque indisponível",
                f"O produto '{produto.nome}' não tem estoque disponível.",
                parent=self
            )
            return
        
        # Verifica se o produto já está no carrinho
        for item in self.itens_carrinho:
            if item.produto_id == produto.id:
                # Já está no carrinho, aumenta a quantidade
                if item.quantidade < produto.estoque:
                    item.quantidade += 1
                    item.calcular_subtotal()
                    self._atualizar_lista_carrinho()
                    self._limpar_busca()
                    messagebox.showinfo(
                        "Quantidade atualizada",
                        f"Quantidade de '{produto.nome}' aumentada para {item.quantidade}.",
                        parent=self
                    )
                else:
                    messagebox.showwarning(
                        "Estoque insuficiente",
                        f"Não há estoque suficiente. Disponível: {produto.estoque}",
                        parent=self
                    )
                return
        
        # Produto novo no carrinho
        item = ItemVenda(
            produto_id=produto.id,
            quantidade=1,
            preco_unitario=produto.preco_venda,
            produto_nome=f"{produto.nome} ({produto.tamanho or ''} {produto.cor or ''})"
        )
        item.calcular_subtotal()
        
        self.itens_carrinho.append(item)
        self._atualizar_lista_carrinho()
        self._limpar_busca()
        
        messagebox.showinfo(
            "Produto adicionado",
            f"'{produto.nome}' adicionado ao carrinho!",
            parent=self
        )
    
    def _limpar_busca(self):
        """Limpa o campo de busca e foca nele."""
        self.entry_busca_produto.delete(0, tk.END)
        self.entry_busca_produto.focus()
    
    # =========================
    # GERENCIAMENTO DO CARRINHO
    # =========================
    
    def _atualizar_lista_carrinho(self):
        """Atualiza a exibição da lista do carrinho."""
        # Limpa a árvore
        for item in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(item)
        
        # Adiciona os itens
        for i, item in enumerate(self.itens_carrinho):
            self.tree_carrinho.insert("", tk.END, values=(
                item.produto_nome,
                item.quantidade,
                formatar_moeda(item.preco_unitario),
                formatar_moeda(item.subtotal)
            ), tags=(i,))
        
        self._atualizar_totais()
    
    def _atualizar_totais(self):
        """Atualiza os valores de subtotal, desconto e total."""
        # Calcula subtotal
        subtotal = sum(item.subtotal for item in self.itens_carrinho)
        
        # Pega desconto
        try:
            desconto = normalizar_numero(self.entry_desconto.get())
            if desconto < 0:
                desconto = 0
            if desconto > subtotal:
                desconto = subtotal
        except:
            desconto = 0
        
        # Calcula total
        total = subtotal - desconto
        
        # Atualiza labels
        self.label_subtotal.config(text=formatar_moeda(subtotal))
        self.label_desconto_valor.config(text=formatar_moeda(desconto))
        self.label_total.config(text=formatar_moeda(total))
    
    def _aumentar_quantidade(self):
        """Aumenta a quantidade do item selecionado."""
        selecao = self.tree_carrinho.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um item.", parent=self)
            return
        
        indice = int(self.tree_carrinho.item(selecao[0])["tags"][0])
        item = self.itens_carrinho[indice]
        
        # Busca o produto para verificar estoque
        produto = next(p for p in self.produtos if p.id == item.produto_id)
        
        if item.quantidade >= produto.estoque:
            messagebox.showwarning(
                "Estoque insuficiente",
                f"Não há mais estoque. Disponível: {produto.estoque}",
                parent=self
            )
            return
        
        item.quantidade += 1
        item.calcular_subtotal()
        self._atualizar_lista_carrinho()
    
    def _diminuir_quantidade(self):
        """Diminui a quantidade do item selecionado."""
        selecao = self.tree_carrinho.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um item.", parent=self)
            return
        
        indice = int(self.tree_carrinho.item(selecao[0])["tags"][0])
        item = self.itens_carrinho[indice]
        
        if item.quantidade > 1:
            item.quantidade -= 1
            item.calcular_subtotal()
            self._atualizar_lista_carrinho()
        else:
            messagebox.showinfo(
                "Remover item",
                "Para remover o item, use o botão 'Remover Item'.",
                parent=self
            )
    
    def _remover_item(self):
        """Remove o item selecionado do carrinho."""
        selecao = self.tree_carrinho.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um item para remover.", parent=self)
            return
        
        indice = int(self.tree_carrinho.item(selecao[0])["tags"][0])
        item = self.itens_carrinho[indice]
        
        if messagebox.askyesno(
            "Confirmar remoção",
            f"Remover '{item.produto_nome}' do carrinho?",
            parent=self
        ):
            del self.itens_carrinho[indice]
            self._atualizar_lista_carrinho()
    
    # =========================
    # GERENCIAMENTO DE CLIENTE
    # =========================
    
    def _selecionar_cliente(self, event=None):
        """Seleciona um cliente do combobox."""
        indice = self.combo_cliente.current()
        
        if indice == 0:  # "Nenhum cliente"
            self.cliente_selecionado = None
        else:
            self.cliente_selecionado = self.clientes[indice - 1]
    
    def _remover_cliente(self):
        """Remove o cliente selecionado."""
        self.cliente_selecionado = None
        self.combo_cliente.current(0)
        messagebox.showinfo("Cliente removido", "Venda sem cliente vinculado.", parent=self)
    
    def _abrir_cadastro_rapido_cliente(self):
        """Abre janela para cadastro rápido de cliente."""
        janela = tk.Toplevel(self)
        janela.title("Cadastro Rápido de Cliente")
        janela.geometry("400x300")
        janela.transient(self)
        janela.grab_set()
        
        tk.Label(
            janela,
            text="Cadastro Rápido de Cliente",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        frame = tk.Frame(janela, padx=20, pady=10)
        frame.pack(fill="both", expand=True)
        
        # Campos
        tk.Label(frame, text="Nome:*").grid(row=0, column=0, sticky="w", pady=5)
        entry_nome = tk.Entry(frame, width=30)
        entry_nome.grid(row=0, column=1, pady=5)
        entry_nome.focus()
        
        tk.Label(frame, text="Telefone:").grid(row=1, column=0, sticky="w", pady=5)
        entry_telefone = tk.Entry(frame, width=30)
        entry_telefone.grid(row=1, column=1, pady=5)
        
        tk.Label(frame, text="CPF:").grid(row=2, column=0, sticky="w", pady=5)
        entry_cpf = tk.Entry(frame, width=30)
        entry_cpf.grid(row=2, column=1, pady=5)
        
        def salvar_cliente():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showwarning("Atenção", "O nome é obrigatório.", parent=janela)
                return
            
            cliente = Cliente(
                nome=nome,
                telefone=entry_telefone.get().strip() or None,
                cpf_cnpj=entry_cpf.get().strip() or None
            )
            
            try:
                cliente_cadastrado = inserir_cliente(cliente)
                messagebox.showinfo(
                    "Sucesso",
                    f"Cliente '{cliente_cadastrado.nome}' cadastrado!",
                    parent=janela
                )
                self._carregar_clientes()
                
                # Seleciona o cliente recém-cadastrado
                for i, c in enumerate(self.clientes):
                    if c.id == cliente_cadastrado.id:
                        self.combo_cliente.current(i + 1)
                        self.cliente_selecionado = c
                        break
                
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e), parent=janela)
        
        # Botões
        frame_botoes = tk.Frame(janela, pady=10)
        frame_botoes.pack(fill="x", padx=20)
        
        tk.Button(
            frame_botoes,
            text="✅ Salvar",
            command=salvar_cliente,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(
            frame_botoes,
            text="❌ Cancelar",
            command=janela.destroy,
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    # =========================
    # FINALIZAÇÃO
    # =========================
    
    def _finalizar_venda(self):
        """Finaliza a venda e salva no banco de dados."""
        # Validações
        if not self.itens_carrinho:
            messagebox.showwarning(
                "Carrinho vazio",
                "Adicione produtos ao carrinho antes de finalizar.",
                parent=self
            )
            return
        
        # Calcula valores
        subtotal = sum(item.subtotal for item in self.itens_carrinho)
        
        try:
            desconto = normalizar_numero(self.entry_desconto.get())
        except:
            desconto = 0
        
        total = subtotal - desconto
        
        if total < 0:
            messagebox.showerror(
                "Erro",
                "O total não pode ser negativo.",
                parent=self
            )
            return
        
        # Confirma
        mensagem = f"Finalizar venda?\n\n"
        mensagem += f"Total: {formatar_moeda(total)}\n"
        mensagem += f"Forma de pagamento: {self.combo_pagamento.get()}\n"
        
        if self.cliente_selecionado:
            mensagem += f"Cliente: {self.cliente_selecionado.nome}"
        
        if not messagebox.askyesno("Confirmar Venda", mensagem, parent=self):
            return
        
        # Cria a venda
        venda = Venda(
            total=total,
            desconto=desconto,
            forma_pagamento=self.combo_pagamento.get(),
            cliente_id=self.cliente_selecionado.id if self.cliente_selecionado else None,
            itens=self.itens_carrinho.copy()
        )
        
        # Salva no banco
        try:
            venda_id = registrar_venda(venda)
            
            messagebox.showinfo(
                "✅ Venda Finalizada!",
                f"Venda #{venda_id} registrada com sucesso!\n\n"
                f"Total: {formatar_moeda(total)}\n"
                f"Forma de pagamento: {venda.forma_pagamento}",
                parent=self
            )
            
            # Limpa o carrinho para nova venda
            self._limpar_carrinho()
            
            # Recarrega produtos (estoque foi atualizado)
            self._carregar_produtos()
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao finalizar venda",
                f"Não foi possível finalizar a venda:\n\n{str(e)}",
                parent=self
            )
    
    def _limpar_carrinho(self):
        """Limpa o carrinho para uma nova venda."""
        if self.itens_carrinho:
            if not messagebox.askyesno(
                "Limpar carrinho",
                "Tem certeza que deseja limpar o carrinho?",
                parent=self
            ):
                return
        
        self.itens_carrinho = []
        self.cliente_selecionado = None
        self.combo_cliente.current(0)
        self.entry_desconto.delete(0, tk.END)
        self.entry_desconto.insert(0, "0")
        self.combo_pagamento.current(0)
        
        self._atualizar_lista_carrinho()
        self._limpar_busca()