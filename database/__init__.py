"""
Módulo de banco de dados do Sistema PDV
Gerencia conexões e configurações do SQLite
"""

from .conexao import conectar, inicializar_banco

__all__ = ['conectar', 'inicializar_banco']