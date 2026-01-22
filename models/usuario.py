import hashlib

class Usuario:
    """
    Representa um usuário do sistema.
    
    Níveis de acesso:
    - 1: ADMINISTRADOR (acesso total)
    - 2: GERENTE (vendas, produtos, clientes, relatórios)
    - 3: VENDEDOR (apenas PDV e consulta de produtos)
    
    Atributos:
        id: Identificador único do usuário
        nome: Nome completo do usuário
        login: Nome de usuário para login (único)
        senha_hash: Hash SHA-256 da senha
        nivel_acesso: Nível de permissão (1, 2 ou 3)
        ativo: 0 = inativo, 1 = ativo
        data_criacao: Data e hora de criação do usuário
        ultimo_acesso: Data e hora do último login
    """
    
    # Constantes de níveis de acesso
    ADMINISTRADOR = 1
    GERENTE = 2
    VENDEDOR = 3
    
    NIVEIS = {
        1: "Administrador",
        2: "Gerente",
        3: "Vendedor"
    }
    
    def __init__(
        self,
        id=None,
        nome=None,
        login=None,
        senha_hash=None,
        nivel_acesso=3,
        ativo=1,
        data_criacao=None,
        ultimo_acesso=None
    ):
        self.id = id
        self.nome = nome
        self.login = login
        self.senha_hash = senha_hash
        self.nivel_acesso = nivel_acesso
        self.ativo = ativo
        self.data_criacao = data_criacao
        self.ultimo_acesso = ultimo_acesso
    
    @staticmethod
    def gerar_hash_senha(senha):
        """
        Gera o hash SHA-256 de uma senha.
        
        Args:
            senha (str): Senha em texto plano
            
        Returns:
            str: Hash SHA-256 da senha
        """
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()
    
    def verificar_senha(self, senha):
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        
        Args:
            senha (str): Senha em texto plano
            
        Returns:
            bool: True se a senha está correta
        """
        return self.senha_hash == Usuario.gerar_hash_senha(senha)
    
    def get_nivel_nome(self):
        """
        Retorna o nome do nível de acesso.
        
        Returns:
            str: Nome do nível (Administrador, Gerente, Vendedor)
        """
        return Usuario.NIVEIS.get(self.nivel_acesso, "Desconhecido")
    
    def pode_acessar_produtos(self):
        """Verifica se pode acessar o módulo de produtos."""
        return self.nivel_acesso in [Usuario.ADMINISTRADOR, Usuario.GERENTE]
    
    def pode_acessar_clientes(self):
        """Verifica se pode acessar o módulo de clientes."""
        return self.nivel_acesso in [Usuario.ADMINISTRADOR, Usuario.GERENTE]
    
    def pode_acessar_estoque(self):
        """Verifica se pode acessar movimentação de estoque."""
        return self.nivel_acesso == Usuario.ADMINISTRADOR
    
    def pode_acessar_vendas(self):
        """Verifica se pode acessar o PDV."""
        return True  # Todos os níveis podem vender
    
    def pode_gerenciar_usuarios(self):
        """Verifica se pode gerenciar usuários."""
        return self.nivel_acesso == Usuario.ADMINISTRADOR
    
    def pode_cancelar_vendas(self):
        """Verifica se pode cancelar vendas."""
        return self.nivel_acesso in [Usuario.ADMINISTRADOR, Usuario.GERENTE]
    
    def __repr__(self):
        return (
            f"Usuario(id={self.id}, nome='{self.nome}', "
            f"login='{self.login}', nivel={self.get_nivel_nome()})"
        )
