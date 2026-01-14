# API Reference - Sistema PDV

Documentação completa das funções e classes disponíveis no sistema.

## 📦 Módulo: produtos_dao.py

### `inserir_produto(produto: Produto) -> Produto`
Insere um novo produto no banco de dados.

**Parâmetros:**
- `produto` (Produto): Objeto Produto com os dados a serem inseridos

**Retorna:**
- Produto: O mesmo objeto com o campo `id` preenchido

**Exemplo:**
```python
from modelos.produto import Produto
from dao.produtos_dao import inserir_produto

produto = Produto(
    nome="Camiseta Básica",
    categoria="Camisetas",
    tamanho="M",
    cor="Azul",
    preco_custo=15.00,
    preco_venda=39.90,
    estoque=50
)

produto_salvo = inserir_produto(produto)
print(f"Produto cadastrado com ID: {produto_salvo.id}")
```

---

### `atualizar_produto(produto: Produto) -> None`
Atualiza os dados de um produto existente.

**Parâmetros:**
- `produto` (Produto): Objeto Produto com ID e dados atualizados

**Exemplo:**
```python
produto = buscar_produto_por_id(1)
produto.preco_venda = 44.90
atualizar_produto(produto)
```

---

### `listar_produtos(...) -> List[Produto]`
Lista produtos com filtros e ordenação opcionais.

**Parâmetros:**
- `ativos_apenas` (bool): Se True, mostra apenas produtos ativos. Padrão: True
- `filtro_nome` (str): Filtra por nome (busca parcial)
- `filtro_categoria` (str): Filtra por categoria (busca parcial)
- `filtro_codigo` (str): Filtra por código de barras (busca parcial)
- `filtro_tamanho` (str): Filtra por tamanho (busca parcial)
- `filtro_cor` (str): Filtra por cor (busca parcial)
- `preco_min` (float): Preço de venda mínimo
- `preco_max` (float): Preço de venda máximo
- `estoque_baixo` (int): Se informado, filtra produtos com estoque ≤ este valor
- `ordenar_por` (str): Coluna para ordenação. Opções: "nome", "categoria", "preco_venda", "estoque", "tamanho", "cor", "preco_custo". Padrão: "nome"
- `ordem_crescente` (bool): True para crescente, False para decrescente. Padrão: True

**Retorna:**
- List[Produto]: Lista de produtos que atendem aos critérios

**Exemplos:**
```python
# Buscar produtos com estoque baixo (5 ou menos)
produtos = listar_produtos(estoque_baixo=5)

# Buscar produtos entre R$ 50 e R$ 100
produtos = listar_produtos(preco_min=50.0, preco_max=100.0)

# Buscar camisetas azuis, ordenadas por preço decrescente
produtos = listar_produtos(
    filtro_nome="camiseta",
    filtro_cor="azul",
    ordenar_por="preco_venda",
    ordem_crescente=False
)

# Buscar todos os produtos, incluindo inativos
todos = listar_produtos(ativos_apenas=False)
```

---

### `buscar_produto_por_id(produto_id: int) -> Produto | None`
Busca um produto específico pelo ID.

**Parâmetros:**
- `produto_id` (int): ID do produto

**Retorna:**
- Produto ou None: Objeto Produto se encontrado, None caso contrário

---

### `buscar_produto_por_codigo_barras(codigo_barras: str) -> Produto | None`
Busca um produto pelo código de barras (apenas produtos ativos).

**Parâmetros:**
- `codigo_barras` (str): Código de barras do produto

**Retorna:**
- Produto ou None: Objeto Produto se encontrado, None caso contrário

---

### `desativar_produto(produto_id: int) -> None`
Desativa um produto (soft delete).

**Parâmetros:**
- `produto_id` (int): ID do produto a ser desativado

---

### `reativar_produto(produto_id: int) -> None`
Reativa um produto que estava desativado.

**Parâmetros:**
- `produto_id` (int): ID do produto a ser reativado

---

## 👥 Módulo: clientes_dao.py

### `inserir_cliente(cliente: Cliente) -> Cliente`
Cadastra um novo cliente no banco de dados.

**Parâmetros:**
- `cliente` (Cliente): Objeto Cliente com os dados

**Retorna:**
- Cliente: O objeto com ID preenchido

**Raises:**
- ValueError: Se o nome não foi informado ou CPF/CNPJ já existe

**Exemplo:**
```python
from modelos.cliente import Cliente
from dao.clientes_dao import inserir_cliente

cliente = Cliente(
    nome="Maria Santos",
    cpf_cnpj="123.456.789-00",
    telefone="(86) 98888-8888",
    email="maria@email.com",
    endereco="Rua das Flores, 123",
    cidade="Teresina",
    estado="PI",
    cep="64000-000"
)

cliente_cadastrado = inserir_cliente(cliente)
print(f"Cliente cadastrado com ID: {cliente_cadastrado.id}")
```

---

### `atualizar_cliente(cliente: Cliente) -> None`
Atualiza os dados de um cliente existente.

**Parâmetros:**
- `cliente` (Cliente): Objeto Cliente com ID e dados atualizados

**Raises:**
- ValueError: Se o ID não foi informado, cliente não existe, ou CPF/CNPJ duplicado

---

### `buscar_cliente_por_id(cliente_id: int) -> Cliente | None`
Busca um cliente pelo ID.

**Parâmetros:**
- `cliente_id` (int): ID do cliente

**Retorna:**
- Cliente ou None: Objeto Cliente se encontrado

---

### `buscar_cliente_por_cpf_cnpj(cpf_cnpj: str) -> Cliente | None`
Busca um cliente pelo CPF ou CNPJ (apenas ativos).

**Parâmetros:**
- `cpf_cnpj` (str): CPF ou CNPJ do cliente

**Retorna:**
- Cliente ou None: Objeto Cliente se encontrado

---

### `listar_clientes(...) -> List[Cliente]`
Lista clientes com opções de filtros.

**Parâmetros:**
- `ativos_apenas` (bool): Se True, mostra apenas clientes ativos. Padrão: True
- `filtro_nome` (str): Filtra por nome (busca parcial)
- `filtro_cpf_cnpj` (str): Filtra por CPF/CNPJ (busca parcial)
- `filtro_telefone` (str): Filtra por telefone (busca parcial)
- `ordenar_por` (str): Coluna para ordenação. Opções: "nome", "cidade", "data_cadastro", "cpf_cnpj". Padrão: "nome"
- `ordem_crescente` (bool): True para crescente, False para decrescente. Padrão: True

**Retorna:**
- List[Cliente]: Lista de clientes

**Exemplos:**
```python
# Buscar clientes com "Silva" no nome
clientes = listar_clientes(filtro_nome="Silva")

# Buscar todos os clientes, incluindo inativos
todos = listar_clientes(ativos_apenas=False)

# Buscar por telefone
clientes = listar_clientes(filtro_telefone="98888")
```

---

### `desativar_cliente(cliente_id: int) -> None`
Desativa um cliente (soft delete).

---

### `reativar_cliente(cliente_id: int) -> None`
Reativa um cliente que estava desativado.

---

### `obter_total_clientes_ativos() -> int`
Retorna o total de clientes ativos no sistema.

**Retorna:**
- int: Número de clientes ativos

---

### `obter_historico_compras_cliente(cliente_id: int) -> List[dict]`
Retorna o histórico de compras de um cliente.

**Parâmetros:**
- `cliente_id` (int): ID do cliente

**Retorna:**
- List[dict]: Lista de dicionários com informações das vendas:
  - `venda_id`: ID da venda
  - `data`: Data da venda
  - `total`: Valor total
  - `forma_pagamento`: Como pagou
  - `desconto`: Desconto aplicado

**Exemplo:**
```python
historico = obter_historico_compras_cliente(1)
for venda in historico:
    print(f"Venda #{venda['venda_id']} - R$ {venda['total']:.2f}")
```

---

### `obter_total_gasto_cliente(cliente_id: int) -> float`
Calcula o total que um cliente já gastou na loja.

**Parâmetros:**
- `cliente_id` (int): ID do cliente

**Retorna:**
- float: Valor total gasto pelo cliente

---

## 🛒 Módulo: vendas_dao.py

### `registrar_venda(venda: Venda) -> int`
Registra uma nova venda no banco de dados.

Esta função realiza 3 operações importantes:
1. Salva a venda (tabela vendas)
2. Salva os itens da venda (tabela itens_venda)
3. Dá baixa no estoque dos produtos vendidos

**Parâmetros:**
- `venda` (Venda): Objeto Venda com os dados da venda e seus itens

**Retorna:**
- int: O ID da venda criada

**Raises:**
- ValueError: Se a venda não tiver itens ou houver estoque insuficiente

**Exemplo:**
```python
from modelos.venda import Venda, ItemVenda

# Criar uma venda
venda = Venda(
    total=150.0,
    desconto=10.0,
    forma_pagamento="DINHEIRO",
    cliente_id=1
)

# Adicionar itens
venda.itens.append(ItemVenda(
    produto_id=1,
    quantidade=2,
    preco_unitario=50.0,
    subtotal=100.0
))

venda.itens.append(ItemVenda(
    produto_id=2,
    quantidade=3,
    preco_unitario=20.0,
    subtotal=60.0
))

# Registrar no banco
venda_id = registrar_venda(venda)
print(f"Venda registrada com ID: {venda_id}")
```

---

### `buscar_venda_por_id(venda_id: int) -> Venda | None`
Busca uma venda pelo ID, incluindo todos os seus itens.

**Parâmetros:**
- `venda_id` (int): ID da venda

**Retorna:**
- Venda ou None: Objeto Venda com todos os itens ou None se não encontrar

---

### `listar_vendas(...) -> List[Venda]`
Lista vendas com opção de filtrar por período.

**Parâmetros:**
- `data_inicial` (str): Data inicial no formato "YYYY-MM-DD" (opcional)
- `data_final` (str): Data final no formato "YYYY-MM-DD" (opcional)
- `incluir_canceladas` (bool): Se True, mostra vendas canceladas também. Padrão: False

**Retorna:**
- List[Venda]: Lista de objetos Venda (sem os itens, apenas o cabeçalho)

**Exemplo:**
```python
from datetime import date

# Listar todas as vendas de hoje
hoje = date.today().strftime("%Y-%m-%d")
vendas = listar_vendas(data_inicial=hoje, data_final=hoje)

# Listar vendas de dezembro de 2025
vendas = listar_vendas(
    data_inicial="2025-12-01",
    data_final="2025-12-31"
)

# Listar todas as vendas, incluindo canceladas
todas = listar_vendas(incluir_canceladas=True)
```

---

### `cancelar_venda(venda_id: int) -> None`
Cancela uma venda e devolve os produtos ao estoque.

**Parâmetros:**
- `venda_id` (int): ID da venda a ser cancelada

**Raises:**
- ValueError: Se a venda não existir ou já estiver cancelada

---

### `obter_total_vendas_periodo(data_inicial: str, data_final: str) -> float`
Calcula o total de vendas em um período.

**Parâmetros:**
- `data_inicial` (str): Data inicial no formato "YYYY-MM-DD"
- `data_final` (str): Data final no formato "YYYY-MM-DD"

**Retorna:**
- float: Valor total vendido no período

**Exemplo:**
```python
# Total de vendas em dezembro de 2025
total = obter_total_vendas_periodo("2025-12-01", "2025-12-31")
print(f"Total vendido: R$ {total:.2f}")
```

---

## 📊 Módulo: estoque_dao.py

### `registrar_entrada(produto_id: int, quantidade: int, observacao: str = None) -> None`
Registra uma entrada de estoque para um produto.

**Parâmetros:**
- `produto_id` (int): ID do produto
- `quantidade` (int): Quantidade a adicionar (deve ser > 0)
- `observacao` (str): Observação opcional

**Raises:**
- ValueError: Se quantidade ≤ 0

---

### `registrar_saida(produto_id: int, quantidade: int, observacao: str = None) -> None`
Registra uma saída de estoque para um produto.

**Parâmetros:**
- `produto_id` (int): ID do produto
- `quantidade` (int): Quantidade a remover (deve ser > 0)
- `observacao` (str): Observação opcional

**Raises:**
- ValueError: Se quantidade ≤ 0, produto não encontrado, ou estoque insuficiente

---

### `listar_movimentacoes(produto_id: int = None) -> List[sqlite3.Row]`
Lista movimentações de estoque.

**Parâmetros:**
- `produto_id` (int): Se informado, filtra pelo produto. Se None, lista todas

**Retorna:**
- List[Row]: Lista de movimentações com informações do produto

---

## 🔧 Módulo: validadores.py

### `normalizar_numero(texto: str) -> float`
Converte um número em formato brasileiro (com vírgula) para o formato Python/banco de dados (com ponto).

**Parâmetros:**
- `texto` (str): O texto digitado pelo usuário

**Retorna:**
- float: O número convertido

**Raises:**
- ValueError: Se o texto não for um número válido

**Exemplos:**
```python
normalizar_numero("10,50")      # → 10.50
normalizar_numero("10.50")      # → 10.50
normalizar_numero("1.250,99")   # → 1250.99
normalizar_numero("")           # → 0.0
```

---

### `formatar_moeda(valor: float) -> str`
Formata um número para o padrão brasileiro de moeda.

**Parâmetros:**
- `valor` (float): O valor numérico a ser formatado

**Retorna:**
- str: O valor formatado como string no padrão brasileiro

**Exemplos:**
```python
formatar_moeda(1234.50)   # → "R$ 1.234,50"
formatar_moeda(10.5)      # → "R$ 10,50"
formatar_moeda(0)         # → "R$ 0,00"
```

---

## 🎨 Módulo: conexao.py

### `conectar() -> sqlite3.Connection`
Conecta ao banco e garante que as tabelas existam.

**Retorna:**
- Connection: Conexão SQLite configurada com:
  - `row_factory = sqlite3.Row` (acesso por nome de coluna)
  - `PRAGMA foreign_keys = ON` (chaves estrangeiras habilitadas)

**Exemplo:**
```python
from banco.conexao import conectar

conexao = conectar()
cursor = conexao.cursor()
cursor.execute("SELECT * FROM produtos WHERE id = ?", (1,))
produto = cursor.fetchone()
print(produto["nome"])  # Acesso por nome da coluna
conexao.close()
```

---

### `inicializar_banco(conexao: sqlite3.Connection) -> None`
Executa o script SQL de inicialização do banco.

**Parâmetros:**
- `conexao` (Connection): Conexão SQLite aberta

**Raises:**
- FileNotFoundError: Se o arquivo init_db.sql não for encontrado
- sqlite3.Error: Se houver erro na execução do SQL

---

## 📝 Classes de Modelo

### Classe: `Produto`
```python
class Produto:
    def __init__(
        self,
        id=None,
        codigo_barras=None,
        nome=None,
        categoria=None,
        tamanho=None,
        cor=None,
        preco_custo=None,
        preco_venda=None,
        estoque=0,
        ativo=1
    )
```

---

### Classe: `Cliente`
```python
class Cliente:
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
    )
    
    def nome_completo_com_doc(self) -> str:
        """Retorna nome com CPF/CNPJ se houver"""
    
    def endereco_completo(self) -> str | None:
        """Retorna endereço completo formatado"""
```

---

### Classe: `Venda`
```python
class Venda:
    def __init__(
        self,
        id=None,
        data=None,
        total=0.0,
        desconto=0.0,
        forma_pagamento="DINHEIRO",
        observacao=None,
        cliente_id=None,
        usuario_id=None,
        cancelada=0,
        itens=None
    )
```

---

### Classe: `ItemVenda`
```python
class ItemVenda:
    def __init__(
        self,
        id=None,
        venda_id=None,
        produto_id=None,
        quantidade=1,
        preco_unitario=0.0,
        subtotal=0.0,
        produto_nome=None
    )
    
    def calcular_subtotal(self) -> float:
        """Calcula o subtotal do item (quantidade × preço unitário)"""
```

---

## 🔄 Constantes

### Formas de Pagamento
```python
FORMAS_PAGAMENTO = [
    "DINHEIRO",
    "PIX",
    "CARTAO_DEBITO",
    "CARTAO_CREDITO"
]
```

### Tipos de Movimentação
```python
TIPOS_MOVIMENTACAO = [
    "ENTRADA",
    "SAIDA"
]
```

---

**Documento mantido por:** Sistema PDV Team  
**Última atualização:** Janeiro 2026