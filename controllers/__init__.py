"""
Controladores do Sistema PDV
Fazem a ponte entre Models e Views
"""

from .produto_controller import ProdutoController
from .cliente_controller import ClienteController
from .venda_controller import VendaController
from .estoque_controller import EstoqueController
from .usuario_controller import UsuarioController

__all__ = [
    'ProdutoController',
    'ClienteController',
    'VendaController',
    'EstoqueController',
    'UsuarioController'
]