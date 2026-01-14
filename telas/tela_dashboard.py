import tkinter as tk
from tkinter import ttk
from datetime import datetime

from dao.vendas_dao import (
    obter_vendas_hoje,
    obter_vendas_mes_atual,
    obter_vendas_por_forma_pagamento,
    obter_produtos_mais_vendidos,
    obter_vendas_ultimos_dias,
    obter_estatisticas_gerais
)
from utils.validadores import formatar_moeda


class TelaDashboard(tk.Toplevel):
    """
    Dashboard de vendas com estatísticas e gráficos.
    
    Mostra:
    - Vendas de hoje e do mês
    - Top 5 produtos mais vendidos
    - Vendas por forma de pagamento
    - Histórico dos últimos 7 dias
    - Estatísticas gerais do sistema
    """
    
    def __init__(self, master=None, usuario_logado=None):
        super().__init__(master)
        self.title("📊 Dashboard de Vendas")
        self.geometry("1200x700")
        
        self.usuario_logado = usuario_logado
        
        # Cores do tema
        self.COR_PRIMARIA = "#2196F3"
        self.COR_SUCESSO = "#4CAF50"
        self.COR_AVISO = "#FF9800"
        self.COR_PERIGO = "#f44336"
        self.COR_FUNDO_CARD = "#f5f5f5"
        
        self._criar_widgets()
        self._carregar_dados()
    
    def _criar_widgets(self):
        """Cria todos os elementos da interface."""
        
        # Frame principal com scroll
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.frame_principal = tk.Frame(canvas, bg="white")
        
        self.frame_principal.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_principal, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cabeçalho
        frame_header = tk.Frame(self.frame_principal, bg=self.COR_PRIMARIA)
        frame_header.pack(fill="x", padx=0, pady=0)
        
        tk.Label(
            frame_header,
            text="📊 Dashboard de Vendas",
            font=("Arial", 18, "bold"),
            bg=self.COR_PRIMARIA,
            fg="white"
        ).pack(pady=15, padx=20, side="left")
        
        # Data e hora
        self.label_datetime = tk.Label(
            frame_header,
            text="",
            font=("Arial", 10),
            bg=self.COR_PRIMARIA,
            fg="white"
        )
        self.label_datetime.pack(pady=15, padx=20, side="right")
        self._atualizar_datetime()
        
        # Botão atualizar
        tk.Button(
            frame_header,
            text="🔄 Atualizar",
            command=self._carregar_dados,
            bg="white",
            fg=self.COR_PRIMARIA,
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief="flat",
            padx=15,
            pady=5
        ).pack(side="right", padx=10)
        
        # Container de conteúdo
        frame_conteudo = tk.Frame(self.frame_principal, bg="white")
        frame_conteudo.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Linha 1: Cards de resumo
        frame_cards = tk.Frame(frame_conteudo, bg="white")
        frame_cards.pack(fill="x", pady=(0, 20))
        
        self._criar_cards_resumo(frame_cards)
        
        # Linha 2: Gráficos principais
        frame_graficos = tk.Frame(frame_conteudo, bg="white")
        frame_graficos.pack(fill="both", expand=True)
        
        # Coluna esquerda: Produtos mais vendidos
        frame_esquerda = tk.Frame(frame_graficos, bg="white")
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self._criar_top_produtos(frame_esquerda)
        
        # Coluna direita: Formas de pagamento
        frame_direita = tk.Frame(frame_graficos, bg="white")
        frame_direita.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self._criar_formas_pagamento(frame_direita)
        
        # Linha 3: Histórico de vendas
        frame_historico = tk.Frame(frame_conteudo, bg="white")
        frame_historico.pack(fill="x", pady=(20, 0))
        
        self._criar_historico_vendas(frame_historico)
    
    def _criar_cards_resumo(self, parent):
        """Cria os cards de resumo com estatísticas principais."""
        
        # Card 1: Vendas de Hoje
        self.card_hoje = self._criar_card(
            parent,
            "💰 Vendas Hoje",
            "R$ 0,00",
            self.COR_SUCESSO
        )
        self.card_hoje.pack(side="left", fill="both", expand=True, padx=5)
        
        # Card 2: Vendas do Mês
        self.card_mes = self._criar_card(
            parent,
            "📅 Vendas do Mês",
            "R$ 0,00",
            self.COR_PRIMARIA
        )
        self.card_mes.pack(side="left", fill="both", expand=True, padx=5)
        
        # Card 3: Ticket Médio
        self.card_ticket = self._criar_card(
            parent,
            "🎫 Ticket Médio",
            "R$ 0,00",
            self.COR_AVISO
        )
        self.card_ticket.pack(side="left", fill="both", expand=True, padx=5)
        
        # Card 4: Total de Vendas
        self.card_total = self._criar_card(
            parent,
            "📊 Total de Vendas",
            "0",
            self.COR_PERIGO
        )
        self.card_total.pack(side="left", fill="both", expand=True, padx=5)
    
    def _criar_card(self, parent, titulo, valor, cor):
        """Cria um card de estatística."""
        card = tk.Frame(
            parent,
            bg=self.COR_FUNDO_CARD,
            relief="solid",
            borderwidth=1
        )
        
        # Barra colorida no topo
        barra = tk.Frame(card, bg=cor, height=5)
        barra.pack(fill="x")
        
        # Conteúdo
        frame_conteudo = tk.Frame(card, bg=self.COR_FUNDO_CARD)
        frame_conteudo.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        label_titulo = tk.Label(
            frame_conteudo,
            text=titulo,
            font=("Arial", 10),
            bg=self.COR_FUNDO_CARD,
            fg="gray"
        )
        label_titulo.pack(anchor="w")
        
        # Valor
        label_valor = tk.Label(
            frame_conteudo,
            text=valor,
            font=("Arial", 20, "bold"),
            bg=self.COR_FUNDO_CARD,
            fg="black"
        )
        label_valor.pack(anchor="w", pady=(5, 0))
        
        # Guarda referência ao label do valor
        card.label_valor = label_valor
        
        return card
    
    def _criar_top_produtos(self, parent):
        """Cria a seção de produtos mais vendidos."""
        frame = tk.LabelFrame(
            parent,
            text="🏆 Top 5 Produtos Mais Vendidos",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        frame.pack(fill="both", expand=True)
        
        # Tabela
        colunas = ("posicao", "produto", "quantidade", "valor")
        
        self.tree_produtos = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=5
        )
        
        self.tree_produtos.heading("posicao", text="#")
        self.tree_produtos.heading("produto", text="Produto")
        self.tree_produtos.heading("quantidade", text="Qtd Vendida")
        self.tree_produtos.heading("valor", text="Valor Total")
        
        self.tree_produtos.column("posicao", width=40, anchor="center")
        self.tree_produtos.column("produto", width=250)
        self.tree_produtos.column("quantidade", width=100, anchor="center")
        self.tree_produtos.column("valor", width=120, anchor="e")
        
        self.tree_produtos.pack(fill="both", expand=True)
    
    def _criar_formas_pagamento(self, parent):
        """Cria a seção de vendas por forma de pagamento."""
        frame = tk.LabelFrame(
            parent,
            text="💳 Vendas por Forma de Pagamento",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        frame.pack(fill="both", expand=True)
        
        # Tabela
        colunas = ("forma", "quantidade", "total", "percentual")
        
        self.tree_pagamento = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=5
        )
        
        self.tree_pagamento.heading("forma", text="Forma de Pagamento")
        self.tree_pagamento.heading("quantidade", text="Qtd")
        self.tree_pagamento.heading("total", text="Total")
        self.tree_pagamento.heading("percentual", text="%")
        
        self.tree_pagamento.column("forma", width=200)
        self.tree_pagamento.column("quantidade", width=80, anchor="center")
        self.tree_pagamento.column("total", width=120, anchor="e")
        self.tree_pagamento.column("percentual", width=80, anchor="center")
        
        self.tree_pagamento.pack(fill="both", expand=True)
    
    def _criar_historico_vendas(self, parent):
        """Cria o gráfico de histórico de vendas dos últimos 7 dias."""
        frame = tk.LabelFrame(
            parent,
            text="📈 Histórico dos Últimos 7 Dias",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        frame.pack(fill="both", expand=True)
        
        # Canvas para o gráfico
        self.canvas_grafico = tk.Canvas(
            frame,
            bg="white",
            height=200
        )
        self.canvas_grafico.pack(fill="both", expand=True, pady=10)
    
    def _carregar_dados(self):
        """Carrega todos os dados do dashboard."""
        try:
            # Estatísticas gerais
            stats = obter_estatisticas_gerais()
            
            # Atualiza cards
            vendas_hoje = obter_vendas_hoje()
            self.card_hoje.label_valor.config(text=formatar_moeda(vendas_hoje))
            
            vendas_mes = obter_vendas_mes_atual()
            self.card_mes.label_valor.config(text=formatar_moeda(vendas_mes))
            
            self.card_ticket.label_valor.config(
                text=formatar_moeda(stats["ticket_medio"])
            )
            
            self.card_total.label_valor.config(
                text=str(stats["total_vendas"])
            )
            
            # Atualiza produtos mais vendidos
            self._atualizar_top_produtos()
            
            # Atualiza formas de pagamento
            self._atualizar_formas_pagamento()
            
            # Atualiza histórico
            self._desenhar_grafico_historico()
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def _atualizar_top_produtos(self):
        """Atualiza a lista de produtos mais vendidos."""
        # Limpa tabela
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        
        # Busca dados
        produtos = obter_produtos_mais_vendidos(limite=5)
        
        # Preenche tabela
        for i, produto in enumerate(produtos, 1):
            # Medalhas para os 3 primeiros
            posicao = f"{i}º"
            if i == 1:
                posicao = "🥇"
            elif i == 2:
                posicao = "🥈"
            elif i == 3:
                posicao = "🥉"
            
            self.tree_produtos.insert("", tk.END, values=(
                posicao,
                produto["nome"],
                produto["quantidade"],
                formatar_moeda(produto["valor_total"])
            ))
    
    def _atualizar_formas_pagamento(self):
        """Atualiza a lista de vendas por forma de pagamento."""
        # Limpa tabela
        for item in self.tree_pagamento.get_children():
            self.tree_pagamento.delete(item)
        
        # Busca dados
        formas = obter_vendas_por_forma_pagamento()
        
        if not formas:
            return
        
        # Calcula total
        total_geral = sum(f["total"] for f in formas)
        
        # Preenche tabela
        for forma in formas:
            percentual = (forma["total"] / total_geral * 100) if total_geral > 0 else 0
            
            self.tree_pagamento.insert("", tk.END, values=(
                forma["forma_pagamento"],
                forma["quantidade"],
                formatar_moeda(forma["total"]),
                f"{percentual:.1f}%"
            ))
    
    def _desenhar_grafico_historico(self):
        """Desenha um gráfico de barras simples com o histórico de vendas."""
        # Limpa canvas
        self.canvas_grafico.delete("all")
        
        # Busca dados
        vendas = obter_vendas_ultimos_dias(dias=7)
        
        if not vendas:
            self.canvas_grafico.create_text(
                300, 100,
                text="Nenhuma venda nos últimos 7 dias",
                font=("Arial", 12),
                fill="gray"
            )
            return
        
        # Dimensões
        largura = self.canvas_grafico.winfo_width() or 600
        altura = 180
        margem_esquerda = 50
        margem_direita = 20
        margem_topo = 20
        margem_base = 40
        
        # Área útil
        area_largura = largura - margem_esquerda - margem_direita
        area_altura = altura - margem_topo - margem_base
        
        # Valor máximo para escala
        valor_max = max(v["total"] for v in vendas)
        if valor_max == 0:
            valor_max = 100  # Evita divisão por zero
        
        # Largura de cada barra
        largura_barra = area_largura / len(vendas) * 0.7
        espaco = area_largura / len(vendas) * 0.3
        
        # Desenha as barras
        for i, venda in enumerate(vendas):
            # Calcula posição e altura da barra
            x = margem_esquerda + (i * (largura_barra + espaco))
            altura_barra = (venda["total"] / valor_max) * area_altura if valor_max > 0 else 0
            y1 = margem_topo + area_altura - altura_barra
            y2 = margem_topo + area_altura
            
            # Cor da barra (gradiente de verde)
            cor = self.COR_SUCESSO
            
            # Desenha barra
            self.canvas_grafico.create_rectangle(
                x, y1, x + largura_barra, y2,
                fill=cor,
                outline=cor
            )
            
            # Label da data
            self.canvas_grafico.create_text(
                x + largura_barra/2, y2 + 15,
                text=venda["data"],
                font=("Arial", 8),
                fill="black"
            )
            
            # Valor acima da barra
            if venda["total"] > 0:
                self.canvas_grafico.create_text(
                    x + largura_barra/2, y1 - 10,
                    text=formatar_moeda(venda["total"]),
                    font=("Arial", 8, "bold"),
                    fill=cor
                )
        
        # Linha de base
        self.canvas_grafico.create_line(
            margem_esquerda,
            margem_topo + area_altura,
            largura - margem_direita,
            margem_topo + area_altura,
            fill="gray",
            width=2
        )
    
    def _atualizar_datetime(self):
        """Atualiza a data e hora no cabeçalho."""
        agora = datetime.now()
        texto = agora.strftime("%d/%m/%Y %H:%M:%S")
        self.label_datetime.config(text=texto)
        
        # Atualiza a cada segundo
        self.after(1000, self._atualizar_datetime)


if __name__ == "__main__":
    # Teste da tela
    root = tk.Tk()
    root.withdraw()
    
    app = TelaDashboard(root)
    app.mainloop()