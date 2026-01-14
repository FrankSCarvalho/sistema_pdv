# Arquitetura do Sistema PDV

## 📐 Visão Geral da Arquitetura

O sistema PDV segue uma arquitetura em camadas (Layered Architecture) com separação clara de responsabilidades, utilizando o padrão DAO (Data Access Object) para abstração do acesso a dados.

## 🏛️ Camadas do Sistema

```
┌─────────────────────────────────────────┐
│         CAMADA DE APRESENTAÇÃO          │
│         (Interface Gráfica)             │
│  - tela_principal.py                    │
│  - tela_produtos.py                     │
│  - tela_vendas.py                       │
│  - tela_movimentacao.py                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         CAMADA DE NEGÓCIO               │
│         (Modelos e Validações)          │
│  - produto.py                           │
│  - cliente.py                           │
│  - venda.py                             │
│  - validadores.py                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         CAMADA DE ACESSO A DADOS        │
│         (DAO - Data Access Objects)     │
│  - produtos_dao.py                      │
│  - clientes_dao.py                      │
│  - vendas_dao.py                        │
│  - estoque_dao.py                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         CAMADA DE PERSISTÊNCIA          │
│         (Banco de Dados)                │
│  - conexao.py                           │
│  - init_db.sql                          │
│  - estoque.db (SQLite)                  │
└─────────────────────────────────────────┘
```

## 🎯 Padrões de Projeto Utilizados

### 1. DAO (Data Access Object)
**Objetivo:** Abstrair e encapsular todo o acesso à fonte de dados.

**Implementação:**
- Cada entidade principal tem seu próprio DAO
- DAOs fornecem operações CRUD e consultas específicas
- Isolamento completo da lógica de banco de dados

**Exemplo:**
```python
# produtos_dao.py
def inserir_produto(produto: Produto) -> Produto:
    """Insere produto no banco e retorna com ID"""
    conexao = conectar()
    cursor = conexao.cursor()
    # SQL e lógica de inserção
    return produto

def listar_produtos(filtros...) -> List[Produto]:
    """Lista produtos com filtros opcionais"""
    # Lógica de consulta com filtros dinâmicos
    return produtos
```

### 2. Model (Modelo de Domínio)
**Objetivo:** Representar entidades do negócio como objetos Python.

**Características:**
- Classes simples com atributos
- Métodos auxiliares para formatação
- Sem lógica de persistência

**Exemplo:**
```python
# cliente.py
class Cliente:
    def __init__(self, id=None, nome=None, cpf_cnpj=None, ...):
        self.id = id
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        # ...
    
    def nome_completo_com_doc(self):
        """Retorna nome formatado com documento"""
        if self.cpf_cnpj:
            tipo = "CPF" if len(...) == 11 else "CNPJ"
            return f"{self.nome} ({tipo}: {self.cpf_cnpj})"
        return self.nome
```

### 3. Soft Delete
**Objetivo:** Preservar dados históricos sem excluir fisicamente.

**Implementação:**
- Campo `ativo` em tabelas principais (produtos, clientes)
- Funções `desativar()` e `reativar()`
- Filtros consideram status ativo/inativo

**Benefícios:**
- Histórico preservado
- Possibilidade de reativação
- Integridade referencial mantida

### 4. Transaction Script
**Objetivo:** Organizar lógica de negócio em procedimentos.

**Exemplo - Finalizar Venda:**
```python
def registrar_venda(venda: Venda):
    conexao = conectar()
    try:
        # 1. Inserir cabeçalho da venda
        cursor.execute("INSERT INTO vendas ...")
        venda_id = cursor.lastrowid
        
        # 2. Inserir itens da venda
        for item in venda.itens:
            # Validar estoque
            # Inserir item
            # Dar baixa no estoque
        
        # 3. Commit de tudo junto
        conexao.commit()
        return venda_id
        
    except Exception as e:
        # Rollback em caso de erro
        conexao.rollback()
        raise e
```

## 🔄 Fluxo de Dados

### Exemplo: Cadastro de Produto

```
1. USUÁRIO digita dados na TelaProdutos
   ↓
2. TELA valida entrada básica (campos obrigatórios)
   ↓
3. TELA cria objeto Produto
   ↓
4. TELA chama produtos_dao.inserir_produto(produto)
   ↓
5. DAO abre conexão com banco
   ↓
6. DAO executa INSERT SQL
   ↓
7. DAO retorna produto com ID preenchido
   ↓
8. TELA atualiza interface e mostra mensagem
```

### Exemplo: Realizar Venda

```
1. USUÁRIO adiciona produtos ao carrinho (TelaProdas)
   ↓
2. TELA mantém lista de ItemVenda em memória
   ↓
3. USUÁRIO clica "Finalizar Venda"
   ↓
4. TELA valida carrinho não vazio
   ↓
5. TELA cria objeto Venda com itens
   ↓
6. TELA chama vendas_dao.registrar_venda(venda)
   ↓
7. DAO inicia transação
   ↓
8. DAO insere venda (tabela vendas)
   ↓
9. DAO insere cada item (tabela itens_venda)
   ↓
10. DAO valida estoque de cada produto
    ↓
11. DAO dá baixa no estoque (UPDATE produtos)
    ↓
12. DAO faz COMMIT da transação
    ↓
13. TELA recebe confirmação e limpa carrinho
```

## 🗄️ Modelo de Dados

### Diagrama ER (Entidade-Relacionamento)

```
┌─────────────────┐         ┌─────────────────┐
│    CLIENTES     │         │    PRODUTOS     │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ nome            │         │ codigo_barras   │
│ cpf_cnpj (UQ)   │         │ nome            │
│ telefone        │         │ categoria       │
│ email           │         │ tamanho         │
│ endereco        │         │ cor             │
│ cidade          │         │ preco_custo     │
│ estado          │         │ preco_venda     │
│ cep             │         │ estoque         │
│ observacoes     │         │ ativo           │
│ data_cadastro   │         └─────────────────┘
│ ativo           │                  │
└─────────────────┘                  │
         │                           │
         │ 1                         │
         │                           │
         │ N                         │ 1
         ↓                           │
┌─────────────────┐                  │
│     VENDAS      │                  │
├─────────────────┤                  │
│ id (PK)         │                  │
│ data            │                  │
│ total           │                  │
│ desconto        │                  │ N
│ forma_pagamento │                  ↓
│ observacao      │         ┌─────────────────┐
│ cliente_id (FK) │────────→│  ITENS_VENDA    │
│ usuario_id      │         ├─────────────────┤
│ cancelada       │         │ id (PK)         │
└─────────────────┘         │ venda_id (FK)   │
         │                  │ produto_id (FK) │
         │ 1                │ quantidade      │
         │                  │ preco_unitario  │
         │ N                │ subtotal        │
         ↓                  └─────────────────┘
┌──────────────────────┐
│ MOVIMENTACOES_ESTOQUE│
├──────────────────────┤
│ id (PK)              │
│ produto_id (FK)      │
│ tipo                 │
│ quantidade           │
│ data                 │
│ observacao           │
└──────────────────────┘
```

### Relacionamentos

1. **Cliente → Vendas (1:N)**
   - Um cliente pode ter várias vendas
   - Uma venda pode ter zero ou um cliente

2. **Venda → Itens_Venda (1:N)**
   - Uma venda tem um ou mais itens
   - Cada item pertence a uma única venda

3. **Produto → Itens_Venda (1:N)**
   - Um produto pode estar em vários itens de venda
   - Cada item de venda referencia um único produto

4. **Produto → Movimentacoes_Estoque (1:N)**
   - Um produto pode ter várias movimentações
   - Cada movimentação pertence a um único produto

## 🔐 Integridade e Consistência

### Foreign Keys (Chaves Estrangeiras)
```sql
PRAGMA foreign_keys = ON;  -- Habilitado em todas as conexões
```

**Benefícios:**
- Impede exclusão de produtos com vendas
- Garante que itens de venda referenciem produtos válidos
- Mantém consistência referencial

### Transações
**Operações Críticas com Transação:**
- Registro de venda (múltiplas inserções + updates)
- Cancelamento de venda (update + devolução de estoque)
- Movimentação de estoque (insert + update)

**Padrão:**
```python
try:
    # Operações múltiplas
    conexao.commit()
except Exception:
    conexao.rollback()
    raise
finally:
    conexao.close()
```

### Validações em Camadas

**1. Interface (Tela):**
- Campos obrigatórios preenchidos
- Formato básico de entrada

**2. Modelo/Validadores:**
- Normalização de valores (vírgula → ponto)
- Formatação de moeda
- Validação de tipos

**3. DAO:**
- Regras de negócio (estoque suficiente)
- Unicidade (CPF, código de barras)
- Constraints do banco

**4. Banco de Dados:**
- CHECK constraints
- NOT NULL
- UNIQUE
- Foreign Keys

## 🎨 Interface Gráfica (Tkinter)

### Estrutura de uma Tela

```python
class TelaProdutos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        # Configurações da janela
        self._criar_widgets()
        self._carregar_dados()
    
    def _criar_widgets(self):
        # Criação de frames, labels, entries, buttons
        # Organização com pack/grid
        # Binding de eventos
    
    def _carregar_dados(self):
        # Busca dados via DAO
        # Popula interface
    
    def _salvar(self):
        # Coleta dados da interface
        # Valida
        # Chama DAO
        # Atualiza interface
```

### Componentes Principais

**1. Frames:**
- Organização lógica da interface
- LabelFrame para grupos visuais

**2. Treeview (Tabelas):**
- Exibição de listas
- Seleção de itens
- Ordenação clicável

**3. Entry/Combobox:**
- Entrada de dados
- Seleção de opções

**4. Buttons:**
- Ações do usuário
- Cores para destacar ações críticas

## 🚀 Performance e Otimização

### Índices no Banco de Dados

```sql
-- Produtos
CREATE INDEX idx_produtos_codigo_barras ON produtos(codigo_barras);
CREATE INDEX idx_produtos_nome ON produtos(nome);

-- Clientes
CREATE INDEX idx_clientes_nome ON clientes(nome);
CREATE INDEX idx_clientes_cpf_cnpj ON clientes(cpf_cnpj);
CREATE INDEX idx_clientes_telefone ON clientes(telefone);

-- Vendas
CREATE INDEX idx_vendas_data ON vendas(data);
CREATE INDEX idx_vendas_cliente_id ON vendas(cliente_id);

-- Itens Venda
CREATE INDEX idx_itens_venda_venda_id ON itens_venda(venda_id);
CREATE INDEX idx_itens_venda_produto_id ON itens_venda(produto_id);

-- Movimentações
CREATE INDEX idx_mov_estoque_produto ON movimentacoes_estoque(produto_id);
CREATE INDEX idx_mov_estoque_data ON movimentacoes_estoque(data);
```

### Paginação

**Estratégia:**
- Busca TODOS os registros filtrados
- Armazena em memória (self.produtos_carregados)
- Exibe apenas página atual (slice da lista)

**Benefícios:**
- Ordenação instantânea (sem nova query)
- Navegação rápida entre páginas
- Filtros aplicados uma única vez

### Busca em Tempo Real com Debounce

```python
def _agendar_busca_tempo_real(self, event=None):
    # Cancela timer anterior
    if self.timer_busca:
        self.after_cancel(self.timer_busca)
    
    # Agenda nova busca para 500ms
    self.timer_busca = self.after(500, self._aplicar_filtros)
```

**Benefícios:**
- Evita queries excessivas durante digitação
- Experiência fluida para o usuário
- Reduz carga no banco

## 🔧 Extensibilidade

### Adicionar Nova Entidade

**1. Criar Modelo:**
```python
# modelos/fornecedor.py
class Fornecedor:
    def __init__(self, id=None, nome=None, ...):
        self.id = id
        self.nome = nome
```

**2. Criar Tabela:**
```sql
-- banco/init_db.sql
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ...
);
```

**3. Criar DAO:**
```python
# dao/fornecedores_dao.py
def inserir_fornecedor(fornecedor):
    # Lógica de inserção

def listar_fornecedores():
    # Lógica de listagem
```

**4. Criar Tela:**
```python
# telas/tela_fornecedores.py
class TelaFornecedores(tk.Toplevel):
    # Interface gráfica
```

**5. Adicionar ao Menu:**
```python
# telas/tela_principal.py
ttk.Button(
    frame,
    text="Fornecedores",
    command=self._abrir_fornecedores
).pack()
```

## 📊 Diagrama de Sequência - Finalizar Venda

```
Usuário    TelaPdas    vendas_dao    Banco
   │           │            │           │
   │  Clica   │            │           │
   │ Finalizar│            │           │
   ├──────────→            │           │
   │           │            │           │
   │           │ Valida    │           │
   │           │ Carrinho  │           │
   │           │            │           │
   │           │ Cria Venda│           │
   │           │            │           │
   │           │registrar_ │           │
   │           │venda()     │           │
   │           ├───────────→           │
   │           │            │           │
   │           │            │BEGIN     │
   │           │            │TRANSACTION
   │           │            ├──────────→
   │           │            │           │
   │           │            │INSERT    │
   │           │            │vendas    │
   │           │            ├──────────→
   │           │            │           │
   │           │            │INSERT    │
   │           │            │itens_venda
   │           │            ├──────────→
   │           │            │           │
   │           │            │UPDATE    │
   │           │            │produtos  │
   │           │            │(estoque) │
   │           │            ├──────────→
   │           │            │           │
   │           │            │COMMIT    │
   │           │            ├──────────→
   │           │            │           │
   │           │ venda_id   │           │
   │           │←───────────┤           │
   │           │            │           │
   │ Mensagem  │            │           │
   │ Sucesso   │            │           │
   │←──────────┤            │           │
   │           │            │           │
```

## 🎓 Boas Práticas Implementadas

1. **Separação de Responsabilidades:** Cada camada tem função específica
2. **DRY (Don't Repeat Yourself):** Funções auxiliares reutilizáveis
3. **Fail-Safe:** Tratamento de exceções em operações críticas
4. **User-Friendly:** Mensagens claras e validações preventivas
5. **Manutenibilidade:** Código documentado e estruturado
6. **Escalabilidade:** Arquitetura permite crescimento
7. **Testabilidade:** Camadas independentes facilitam testes

---

**Documento mantido por:** Sistema PDV Team  
**Última atualização:** Janeiro 2026