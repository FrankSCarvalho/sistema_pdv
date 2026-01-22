"""
Views (Telas) do Sistema PDV
Interface gráfica com o usuário
"""

from .tela_principal import TelaPrincipal
from .tela_login import TelaLogin
from .tela_produtos import TelaProdutos
from .tela_vendas import TelaVendas
from .tela_movimentacao import TelaMovimentacao
from .tela_usuarios import TelaUsuarios
from .tela_dashboard import TelaDashboard

__all__ = [
    'TelaPrincipal',
    'TelaLogin',
    'TelaProdutos',
    'TelaVendas',
    'TelaMovimentacao',
    'TelaUsuarios',
    'TelaDashboard'
]