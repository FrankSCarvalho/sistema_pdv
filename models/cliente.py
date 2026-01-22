class Cliente:
    """
    Representa um cliente da loja.
    
    Atributos:
        id: Identificador único do cliente
        nome: Nome completo do cliente
        cpf_cnpj: CPF ou CNPJ do cliente (opcional, pode ser None)
        telefone: Telefone para contato (opcional)
        email: Email do cliente (opcional)
        endereco: Endereço completo (rua, número, complemento)
        cidade: Cidade onde mora
        estado: Estado (UF) - ex: "PI", "SP"
        cep: CEP do endereço
        observacoes: Observações sobre o cliente (ex: "Prefere entregas pela manhã")
        data_cadastro: Data e hora do cadastro (formato: "YYYY-MM-DD HH:MM:SS")
        ativo: 0 = cliente inativo, 1 = cliente ativo
        
    Exemplo de uso:
        cliente = Cliente(
            nome="João Silva",
            cpf_cnpj="123.456.789-00",
            telefone="(86) 99999-9999",
            email="joao@email.com"
        )
    """
    def __init__(
        self,
        id=None,
        nome=None,
        cpf_cnpj=None,
        telefone=None,
        email=None,
        endereco=None,
        cidade=None,
        estado=None,
        cep=None,
        observacoes=None,
        data_cadastro=None,
        ativo=1
    ):
        self.id = id
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.observacoes = observacoes
        self.data_cadastro = data_cadastro
        self.ativo = ativo

    def __repr__(self):
        return (
            f"Cliente(id={self.id}, nome='{self.nome}', "
            f"telefone='{self.telefone}')"
        )
    
    def nome_completo_com_doc(self):
        """
        Retorna o nome do cliente com CPF/CNPJ se houver.
        
        Returns:
            str: "João Silva (CPF: 123.456.789-00)" ou apenas "João Silva"
        """
        if self.cpf_cnpj:
            tipo_doc = "CPF" if len(self.cpf_cnpj.replace(".", "").replace("-", "")) == 11 else "CNPJ"
            return f"{self.nome} ({tipo_doc}: {self.cpf_cnpj})"
        return self.nome
    
    def endereco_completo(self):
        """
        Retorna o endereço completo formatado.
        
        Returns:
            str: Endereço completo ou None se não houver endereço
        """
        partes = []
        
        if self.endereco:
            partes.append(self.endereco)
        
        if self.cidade or self.estado:
            cidade_estado = []
            if self.cidade:
                cidade_estado.append(self.cidade)
            if self.estado:
                cidade_estado.append(self.estado)
            partes.append(" - ".join(cidade_estado))
        
        if self.cep:
            partes.append(f"CEP: {self.cep}")
        
        return ", ".join(partes) if partes else None