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
    def __init__(self, master=None, usuario_logado=None):
        super().__init__(master)
        self.title("Cadastro de Produtos")
        self.geometry("1000x750")  # ← AUMENTEI para 750

        self.produto_selecionado_id = None
        self.produto_selecionado_ativo = True
        
        # Variáveis para controlar a paginação
        self.pagina_atual = 1
        self.itens_por_pagina = 16
        self.total_produtos = 0
        self.produtos_carregados = []
        
        # NOVO: Variáveis para controlar a ordenação
        self.coluna_ordenacao = "nome"  # Coluna atual de ordenação
        self.ordem_crescente = True  # True = crescente, False = decrescente
        
        # NOVO: Variável para controlar o timer da busca em tempo real
        self.timer_busca = None  # Usado para aguardar o usuário parar de digitar

        self._criar_widgets()
        self._carregar_produtos()

    # =========================
    # INTERFACE
    # =========================
    def _criar_widgets(self):
        # ========================================
        # NOVO: Frame de Filtros EXPANDIDO (2 linhas)
        # ========================================
        frame_filtros = tk.LabelFrame(self, text="🔍 Filtros de Pesquisa", padx=10, pady=8)
        frame_filtros.pack(fill="x", padx=10, pady=(5, 0))

        # ===== LINHA 1 de filtros =====
        tk.Label(frame_filtros, text="Nome:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        tk.Label(frame_filtros, text="Categoria:").grid(row=0, column=2, sticky="w", padx=(10, 5))
        tk.Label(frame_filtros, text="Código:").grid(row=0, column=4, sticky="w", padx=(10, 5))

        self.entry_filtro_nome = tk.Entry(frame_filtros, width=25)
        self.entry_filtro_categoria = tk.Entry(frame_filtros, width=18)
        self.entry_filtro_codigo = tk.Entry(frame_filtros, width=18)

        self.entry_filtro_nome.grid(row=0, column=1, padx=5, pady=5)
        self.entry_filtro_categoria.grid(row=0, column=3, padx=5, pady=5)
        self.entry_filtro_codigo.grid(row=0, column=5, padx=5, pady=5)

        # ===== LINHA 2 de filtros (NOVOS) =====
        tk.Label(frame_filtros, text="Tamanho:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        tk.Label(frame_filtros, text="Cor:").grid(row=1, column=2, sticky="w", padx=(10, 5))
        tk.Label(frame_filtros, text="Preço Min:").grid(row=1, column=4, sticky="w", padx=(10, 5))
        tk.Label(frame_filtros, text="Preço Max:").grid(row=1, column=6, sticky="w", padx=(10, 5))

        self.entry_filtro_tamanho = tk.Entry(frame_filtros, width=10)
        self.entry_filtro_cor = tk.Entry(frame_filtros, width=15)
        self.entry_filtro_preco_min = tk.Entry(frame_filtros, width=10)
        self.entry_filtro_preco_max = tk.Entry(frame_filtros, width=10)

        self.entry_filtro_tamanho.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entry_filtro_cor.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_filtro_preco_min.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        self.entry_filtro_preco_max.grid(row=1, column=7, padx=5, pady=5, sticky="w")

        # ===== LINHA 3: Checkbox de estoque baixo e botões =====
        self.var_estoque_baixo = tk.BooleanVar(value=False)
        self.check_estoque_baixo = tk.Checkbutton(
            frame_filtros,
            text="Apenas estoque baixo (≤ 10)",
            variable=self.var_estoque_baixo,
            command=self._aplicar_filtros_automatico
        )
        self.check_estoque_baixo.grid(row=2, column=0, columnspan=3, sticky="w", pady=5)

        # Botão limpar filtros
        btn_limpar_filtro = tk.Button(
            frame_filtros, 
            text="✖ Limpar Filtros", 
            command=self._limpar_filtros,
            cursor="hand2"
        )
        btn_limpar_filtro.grid(row=2, column=5, columnspan=3, padx=5)

        # NOVO: Configurar busca em tempo real (evento KeyRelease)
        # Quando o usuário solta uma tecla, aguarda 500ms e então busca
        for entry in [
            self.entry_filtro_nome,
            self.entry_filtro_categoria,
            self.entry_filtro_codigo,
            self.entry_filtro_tamanho,
            self.entry_filtro_cor,
            self.entry_filtro_preco_min,
            self.entry_filtro_preco_max
        ]:
            entry.bind('<KeyRelease>', self._agendar_busca_tempo_real)

        # ========================================
        # Frame de Cadastro (mantido igual)
        # ========================================
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
            "nome": "Produto ▲",  # ← Indicador de ordenação inicial
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

        # NOVO: Adicionar clique nas colunas para ordenar
        # Colunas que podem ser ordenadas
        colunas_ordenaveis = ["nome", "categoria", "estoque", "preco_venda", "tamanho", "cor", "preco_custo"]
        for col in colunas_ordenaveis:
            self.tree.heading(col, text=titulos[col], command=lambda c=col: self._ordenar_por_coluna(c))

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_produto)
        
        # Frame para controles de paginação
        frame_paginacao = tk.Frame(self)
        frame_paginacao.pack(fill="x", padx=10, pady=5)
        
        self.btn_primeira = tk.Button(
            frame_paginacao, 
            text="<<", 
            command=self._ir_primeira_pagina,
            width=3
        )
        self.btn_primeira.pack(side="left", padx=2)
        
        self.btn_anterior = tk.Button(
            frame_paginacao, 
            text="<", 
            command=self._pagina_anterior,
            width=3
        )
        self.btn_anterior.pack(side="left", padx=2)
        
        self.label_pagina = tk.Label(
            frame_paginacao, 
            text="Página 1 de 1",
            font=("Arial", 10)
        )
        self.label_pagina.pack(side="left", padx=10)
        
        self.btn_proxima = tk.Button(
            frame_paginacao, 
            text=">", 
            command=self._proxima_pagina,
            width=3
        )
        self.btn_proxima.pack(side="left", padx=2)
        
        self.btn_ultima = tk.Button(
            frame_paginacao, 
            text=">>", 
            command=self._ir_ultima_pagina,
            width=3
        )
        self.btn_ultima.pack(side="left", padx=2)
        
        self.label_total = tk.Label(
            frame_paginacao,
            text="Total: 0 produtos",
            font=("Arial", 9)
        )
        self.label_total.pack(side="right", padx=10)
        
        self._atualizar_visibilidade_botoes()

    # =========================
    # NOVAS FUNÇÕES DE BUSCA EM TEMPO REAL
    # =========================
    def _agendar_busca_tempo_real(self, event=None):
        """
        Agenda uma busca para daqui a 500ms.
        Se o usuário continuar digitando, o timer é reiniciado.
        Isso evita fazer muitas buscas enquanto o usuário digita rapidamente.
        """
        # Cancela o timer anterior (se existir)
        if self.timer_busca:
            self.after_cancel(self.timer_busca)
        
        # Agenda uma nova busca para daqui a 500 milissegundos
        self.timer_busca = self.after(500, self._aplicar_filtros_automatico)

    def _aplicar_filtros_automatico(self):
        """
        Aplica os filtros sem precisar clicar em botão.
        Volta para página 1 e recarrega.
        """
        self.pagina_atual = 1
        self._carregar_produtos()

    # =========================
    # NOVA FUNÇÃO DE ORDENAÇÃO
    # =========================
    def _ordenar_por_coluna(self, coluna):
        """
        Ordena a tabela pela coluna clicada.
        Se clicar na mesma coluna, inverte a ordem (crescente/decrescente).
        """
        # Se clicar na mesma coluna, inverte a ordem
        if self.coluna_ordenacao == coluna:
            self.ordem_crescente = not self.ordem_crescente
        else:
            # Se mudar de coluna, começa em ordem crescente
            self.coluna_ordenacao = coluna
            self.ordem_crescente = True
        
        # Atualiza os cabeçalhos para mostrar o indicador de ordenação
        self._atualizar_indicador_ordenacao()
        
        # Recarrega os produtos com a nova ordenação
        self._carregar_produtos()

    def _atualizar_indicador_ordenacao(self):
        """
        Atualiza os cabeçalhos das colunas para mostrar qual está ordenada.
        ▲ = crescente, ▼ = decrescente
        """
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
        
        # Adiciona o indicador na coluna ordenada
        for col in titulos:
            texto = titulos[col]
            if col == self.coluna_ordenacao:
                texto += " ▲" if self.ordem_crescente else " ▼"
            self.tree.heading(col, text=texto)

    # =========================
    # FUNÇÕES DE FILTRO
    # =========================
    def _aplicar_filtros(self):
        """
        Aplica os filtros digitados pelo usuário.
        Volta para a página 1 e recarrega a tabela.
        """
        self.pagina_atual = 1
        self._carregar_produtos()

    def _limpar_filtros(self):
        """
        Limpa todos os campos de filtro.
        Volta para a página 1 e recarrega a tabela completa.
        """
        # Limpa os campos de texto
        self.entry_filtro_nome.delete(0, tk.END)
        self.entry_filtro_categoria.delete(0, tk.END)
        self.entry_filtro_codigo.delete(0, tk.END)
        self.entry_filtro_tamanho.delete(0, tk.END)
        self.entry_filtro_cor.delete(0, tk.END)
        self.entry_filtro_preco_min.delete(0, tk.END)
        self.entry_filtro_preco_max.delete(0, tk.END)
        
        # Desmarca o checkbox de estoque baixo
        self.var_estoque_baixo.set(False)
        
        # Volta para a primeira página
        self.pagina_atual = 1
        
        # Recarrega sem filtros
        self._carregar_produtos()

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
        Carrega TODOS os produtos do banco (aplicando filtros se houver)
        e depois exibe apenas os da página atual.
        """
        # Pega os valores dos filtros
        mostrar_inativos = self.var_mostrar_inativos.get()
        filtro_nome = self.entry_filtro_nome.get()
        filtro_categoria = self.entry_filtro_categoria.get()
        filtro_codigo = self.entry_filtro_codigo.get()
        filtro_tamanho = self.entry_filtro_tamanho.get()
        filtro_cor = self.entry_filtro_cor.get()
        
        # Pega valores de preço (converte para float se houver)
        preco_min = None
        preco_max = None
        
        try:
            texto_min = self.entry_filtro_preco_min.get()
            if texto_min.strip():
                preco_min = normalizar_numero(texto_min)
        except:
            pass  # Ignora erro de conversão
        
        try:
            texto_max = self.entry_filtro_preco_max.get()
            if texto_max.strip():
                preco_max = normalizar_numero(texto_max)
        except:
            pass  # Ignora erro de conversão
        
        # Verifica se o filtro de estoque baixo está marcado
        estoque_baixo = 10 if self.var_estoque_baixo.get() else None
        
        # Busca TODOS os produtos com os filtros e ordenação
        self.produtos_carregados = listar_produtos(
            ativos_apenas=not mostrar_inativos,
            filtro_nome=filtro_nome,
            filtro_categoria=filtro_categoria,
            filtro_codigo=filtro_codigo,
            filtro_tamanho=filtro_tamanho,
            filtro_cor=filtro_cor,
            preco_min=preco_min,
            preco_max=preco_max,
            estoque_baixo=estoque_baixo,
            ordenar_por=self.coluna_ordenacao,
            ordem_crescente=self.ordem_crescente
        )
        
        # Atualiza o total de produtos
        self.total_produtos = len(self.produtos_carregados)
        
        # Atualiza a exibição da tabela com a página atual
        self._atualizar_tabela()
        
        # Atualiza os controles de paginação
        self._atualizar_controles_paginacao()

    # ===== Atualiza apenas a tabela =====
    def _atualizar_tabela(self):
        """
        Atualiza a tabela mostrando apenas os produtos da página atual.
        """
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calcula quais produtos mostrar
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

    # ===== Atualiza os controles de paginação =====
    def _atualizar_controles_paginacao(self):
        """
        Atualiza os botões e labels da paginação.
        """
        import math
        total_paginas = math.ceil(self.total_produtos / self.itens_por_pagina) if self.total_produtos > 0 else 1
        
        # Atualiza o texto da página
        self.label_pagina.config(text=f"Página {self.pagina_atual} de {total_paginas}")
        self.label_total.config(text=f"Total: {self.total_produtos} produtos")
        
        # Habilita/desabilita botões
        if self.pagina_atual <= 1:
            self.btn_anterior.config(state="disabled")
            self.btn_primeira.config(state="disabled")
        else:
            self.btn_anterior.config(state="normal")
            self.btn_primeira.config(state="normal")
        
        if self.pagina_atual >= total_paginas:
            self.btn_proxima.config(state="disabled")
            self.btn_ultima.config(state="disabled")
        else:
            self.btn_proxima.config(state="normal")
            self.btn_ultima.config(state="normal")

    # ===== Navegação entre páginas =====
    def _proxima_pagina(self):
        """Vai para a próxima página."""
        import math
        total_paginas = math.ceil(self.total_produtos / self.itens_por_pagina)
        
        if self.pagina_atual < total_paginas:
            self.pagina_atual += 1
            self._atualizar_tabela()
            self._atualizar_controles_paginacao()

    def _pagina_anterior(self):
        """Volta para a página anterior."""
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self._atualizar_tabela()
            self._atualizar_controles_paginacao()

    def _ir_primeira_pagina(self):
        """Vai para a primeira página."""
        self.pagina_atual = 1
        self._atualizar_tabela()
        self._atualizar_controles_paginacao()

    def _ir_ultima_pagina(self):
        """Vai para a última página."""
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