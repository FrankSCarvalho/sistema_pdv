import tkinter as tk
from tkinter import ttk, messagebox

from telas.tela_produtos import TelaProdutos
from telas.tela_movimentacao import TelaMovimentacao
from telas.tela_vendas import TelaVendas
from telas.tela_usuarios import TelaUsuarios
from telas.tela_dashboard import TelaDashboard

from utils.atualizador import verificar_atualizacao


class TelaPrincipal(tk.Tk):
    def __init__(self, usuario_logado=None):
        super().__init__()
        
        if not usuario_logado:
            messagebox.showerror("Erro", "Usuário não autenticado!")
            self.destroy()
            return
        
        self.usuario_logado = usuario_logado
        
        self.title(f"Sistema PDV - {usuario_logado.nome} ({usuario_logado.get_nivel_nome()})")
        self.geometry("450x400")
        self.resizable(False, False)

        self._criar_widgets()

        self.after(1000, lambda: verificar_atualizacao(self))

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        # Informações do usuário
        frame_usuario = tk.Frame(frame, bg="#e3f2fd", relief="solid", borderwidth=1)
        frame_usuario.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            frame_usuario,
            text=f"👤 {self.usuario_logado.nome}",
            font=("Arial", 11, "bold"),
            bg="#e3f2fd"
        ).pack(pady=5)
        
        tk.Label(
            frame_usuario,
            text=f"Nível: {self.usuario_logado.get_nivel_nome()}",
            font=("Arial", 9),
            bg="#e3f2fd",
            fg="gray"
        ).pack(pady=(0, 5))

        # Título
        titulo = ttk.Label(
            frame,
            text="Controle de Estoque",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Botões de navegação (com controle de acesso)

        # Dashboard - Todos podem ver
        ttk.Button(
                frame,
                text="📊 Dashboard de Vendas",
                width=30,
                command=self._abrir_dashboard
            ).pack(pady=5)

        
        # PDV - Todos podem acessar
        if self.usuario_logado.pode_acessar_vendas():
            ttk.Button(
                frame,
                text="🛒 Vendas (PDV)",
                width=30,
                command=self._abrir_vendas
            ).pack(pady=5)

        # Produtos - Admin e Gerente
        if self.usuario_logado.pode_acessar_produtos():
            ttk.Button(
                frame,
                text="📦 Cadastro de Produtos",
                width=30,
                command=self._abrir_produtos
            ).pack(pady=5)

        # Movimentação de Estoque - Apenas Admin
        if self.usuario_logado.pode_acessar_estoque():
            ttk.Button(
                frame,
                text="📊 Movimentação de Estoque",
                width=30,
                command=self._abrir_movimentacao
            ).pack(pady=5)

        # Gerenciamento de Usuários - Apenas Admin
        if self.usuario_logado.pode_gerenciar_usuarios():
            ttk.Button(
                frame,
                text="👥 Gerenciar Usuários",
                width=30,
                command=self._abrir_usuarios
            ).pack(pady=5)

        # Botão Sair
        ttk.Button(
            frame,
            text="🚪 Sair",
            width=30,
            command=self._sair
        ).pack(pady=15)
        
        # Versão
        tk.Label(
            frame,
            text="Versão 2.0.0 - Sistema com Login",
            font=("Arial", 8),
            fg="gray"
        ).pack(side="bottom")

    def _abrir_vendas(self):
        TelaVendas(self, usuario_logado=self.usuario_logado)

    def _abrir_produtos(self):
        TelaProdutos(self, usuario_logado=self.usuario_logado)

    def _abrir_movimentacao(self):
        TelaMovimentacao(self, usuario_logado=self.usuario_logado)
    
    def _abrir_usuarios(self):
        TelaUsuarios(self, usuario_logado=self.usuario_logado)
    
    def _sair(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente sair do sistema?", parent=self):
            self.destroy()

    def _abrir_dashboard(self):
        TelaDashboard(self, usuario_logado=self.usuario_logado)