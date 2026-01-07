import tkinter as tk
from tkinter import ttk

from telas.tela_produtos import TelaProdutos
from telas.tela_movimentacao import TelaMovimentacao
from telas.tela_vendas import TelaVendas

from utils.atualizador import verificar_atualizacao


class TelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Estoque - Loja de Roupas")
        self.geometry("400x300")
        self.resizable(False, False)

        self._criar_widgets()

        self.after(1000, lambda: verificar_atualizacao(self))

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        titulo = ttk.Label(
            frame,
            text="Controle de Estoque",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        ttk.Button(
            frame,
            text="🛒 Vendas (PDV)",
            width=30,
            command=self._abrir_vendas
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="📦 Cadastro de Produtos",
            width=30,
            command=self._abrir_produtos
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="📊 Movimentação de Estoque",
            width=30,
            command=self._abrir_movimentacao
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="❌ Sair",
            width=30,
            command=self.destroy
        ).pack(pady=15)

    def _abrir_vendas(self):
        TelaVendas(self)

    def _abrir_produtos(self):
        TelaProdutos(self)

    def _abrir_movimentacao(self):
        TelaMovimentacao(self)