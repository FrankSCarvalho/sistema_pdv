# Sistema PDV - Controle de Estoque para Loja de Roupas

## 📋 Visão Geral

Sistema completo de Ponto de Venda (PDV) e controle de estoque desenvolvido em Python com interface gráfica Tkinter e banco de dados SQLite. Projetado especificamente para lojas de roupas, oferecendo gestão de produtos, clientes, vendas e movimentação de estoque.

**Versão Atual:** 1.6.0

## 🎯 Funcionalidades Principais

### 1. **Gestão de Produtos**
- Cadastro completo com código de barras, nome, categoria, tamanho, cor
- Controle de preço de custo e venda
- Gestão de estoque em tempo real
- Sistema de ativação/desativação (soft delete)
- Busca avançada com múltiplos filtros:
  - Nome, categoria, código de barras
  - Tamanho, cor
  - Faixa de preço (mínimo e máximo)
  - Estoque baixo (≤ 10 unidades)
- Ordenação clicável por colunas
- Busca em tempo real (500ms delay)
- Paginação (16 itens por página)
- Cálculo automático de valores totais em estoque

### 2. **Sistema de Vendas (PDV)**
- Interface intuitiva tipo caixinha
- Busca de produtos por código de barras ou nome
- Carrinho de compras com:
  - Adição/remoção de itens
  - Ajuste de quantidades
  - Validação de estoque em tempo real
- Vinculação opcional de clientes
- Cadastro rápido de clientes durante a venda
- Aplicação de descontos
- Múltiplas formas de pagamento:
  - Dinheiro
  - PIX
  - Cartão de Débito
  - Cartão de Crédito
- Baixa automática no estoque após finalização
- Registro detalhado de cada venda

### 3. **Gestão de Clientes**
- Cadastro completo com:
  - Dados pessoais (nome, CPF/CNPJ, telefone, email)
  - Endereço completo (rua, cidade, estado, CEP)
  - Observações personalizadas
- Validação de CPF/CNPJ único
- Sistema de ativação/desativação
- Busca e filtros avançados
- Histórico de compras por cliente
- Cálculo de total gasto por cliente
- Vinculação automática com vendas

### 4. **Movimentação de Estoque**
- Registro de entradas e saídas
- Histórico completo de movimentações
- Observações por movimentação
- Atualização automática do estoque
- Rastreabilidade completa

### 5. **Sistema de Atualização**
- Verificação automática de novas versões
- Integração com GitHub Releases
- Notificação ao usuário
- Download direto da nova versão

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
sistema_pdv/
├── banco/
│   ├── conexao.py          # Gerenciamento de conexão SQLite
│   └── init_db.sql         # Script de inicialização do banco
├── dao/                    # Data Access Objects
│   ├── produtos_dao.py     # Operações de produtos
│   ├── clientes_dao.py     # Operações de clientes
│   ├── vendas_dao.py       # Operações de vendas
│   └── estoque_dao.py      # Operações de estoque
├── modelos/                # Classes de modelo
│   ├── produto.py          # Classe Produto
│   ├── cliente.py          # Classe Cliente
│   └── venda.py            # Classes Venda e ItemVenda
├── telas/                  # Interfaces gráficas
│   ├── tela_principal.py   # Menu principal
│   ├── tela_produtos.py    # Gestão de produtos
│   ├── tela_vendas.py      # PDV
│   └── tela_movimentacao.py # Movimentação de estoque
├── utils/                  # Utilitários
│   ├── validadores.py      # Funções de validação e formatação
│   └── atualizador.py      # Sistema de atualização
├── versao.py               # Controle de versão
└── main.py                 # Ponto de entrada da aplicação
```

### Banco de Dados (SQLite)

#### Tabela: `produtos`
```sql
- id (INTEGER PRIMARY KEY)
- codigo_barras (TEXT UNIQUE)
- nome (TEXT NOT NULL)
- categoria (TEXT)
- tamanho (TEXT)
- cor (TEXT)
- preco_custo (REAL)
- preco_venda (REAL NOT NULL)
- estoque (INTEGER DEFAULT 0)
- ativo (INTEGER DEFAULT 1)
```

#### Tabela: `clientes`
```sql
- id (INTEGER PRIMARY KEY)
- nome (TEXT NOT NULL)
- cpf_cnpj (TEXT UNIQUE)
- telefone (TEXT)
- email (TEXT)
- endereco (TEXT)
- cidade (TEXT)
- estado (TEXT)
- cep (TEXT)
- observacoes (TEXT)
- data_cadastro (TEXT NOT NULL)
- ativo (INTEGER DEFAULT 1)
```

#### Tabela: `vendas`
```sql
- id (INTEGER PRIMARY KEY)
- data (TEXT NOT NULL)
- total (REAL NOT NULL)
- desconto (REAL DEFAULT 0)
- forma_pagamento (TEXT NOT NULL)
- observacao (TEXT)
- cliente_id (INTEGER FK)
- usuario_id (INTEGER)
- cancelada (INTEGER DEFAULT 0)
```

#### Tabela: `itens_venda`
```sql
- id (INTEGER PRIMARY KEY)
- venda_id (INTEGER FK NOT NULL)
- produto_id (INTEGER FK NOT NULL)
- quantidade (INTEGER NOT NULL)
- preco_unitario (REAL NOT NULL)
- subtotal (REAL NOT NULL)
```

#### Tabela: `movimentacoes_estoque`
```sql
- id (INTEGER PRIMARY KEY)
- produto_id (INTEGER FK NOT NULL)
- tipo (TEXT CHECK IN ('ENTRADA', 'SAIDA'))
- quantidade (INTEGER NOT NULL)
- data (TEXT NOT NULL)
- observacao (TEXT)
```

## 🚀 Como Usar

### Instalação

1. **Pré-requisitos:**
   - Python 3.8 ou superior
   - Bibliotecas: tkinter (geralmente incluído), requests

2. **Instalação de dependências:**
```bash
pip install requests
```

3. **Executar o sistema:**
```bash
python main.py
```

### Primeiro Uso

1. O sistema criará automaticamente o banco de dados `estoque.db` na primeira execução
2. Localização do banco:
   - **Windows:** `%LOCALAPPDATA%\EstoqueLoja\estoque.db`
   - **Linux/Mac:** `~/.local/share/estoque_loja/estoque.db`

### Fluxo de Trabalho Recomendado

#### 1. Cadastrar Produtos
- Acesse "📦 Cadastro de Produtos"
- Preencha os dados do produto
- Clique em "Salvar"
- Use filtros para localizar produtos rapidamente

#### 2. Registrar Entrada de Estoque
- Acesse "📊 Movimentação de Estoque"
- Selecione o produto
- Escolha tipo "ENTRADA"
- Informe a quantidade
- Adicione observação (opcional)
- Clique em "Registrar"

#### 3. Realizar Venda
- Acesse "🛒 Vendas (PDV)"
- Digite código de barras ou nome do produto
- Pressione Enter ou clique em "Buscar"
- Produto é adicionado ao carrinho
- Selecione cliente (opcional)
- Aplique desconto se necessário
- Escolha forma de pagamento
- Clique em "FINALIZAR VENDA"

#### 4. Cadastrar Clientes
- Durante uma venda, clique em "➕ Novo Cliente"
- Ou acesse o módulo de clientes (futuro)
- Preencha os dados
- Cliente fica disponível para vendas futuras

## 🔧 Recursos Técnicos

### Padrão de Projeto
- **DAO (Data Access Object):** Separação entre lógica de negócio e acesso a dados
- **MVC Adaptado:** Modelos, Views (telas) e Controllers (DAOs)
- **Soft Delete:** Produtos e clientes são desativados, não excluídos

### Validações
- Normalização de valores monetários (aceita vírgula e ponto)
- Formatação brasileira de moeda (R$ 1.234,56)
- Validação de estoque antes de vendas
- Unicidade de código de barras e CPF/CNPJ
- Verificação de integridade referencial (Foreign Keys)

### Performance
- Índices em colunas frequentemente consultadas
- Busca em tempo real com debounce (500ms)
- Paginação para grandes volumes de dados
- Queries otimizadas com filtros no banco

### Segurança
- PRAGMA foreign_keys habilitado
- Transações para operações críticas
- Rollback automático em caso de erro
- Validação de entrada de dados

## 📊 Relatórios e Consultas

### Consultas Disponíveis via DAO

**Produtos:**
- Listar com filtros múltiplos
- Buscar por ID ou código de barras
- Produtos com estoque baixo
- Ordenação personalizada

**Clientes:**
- Histórico de compras
- Total gasto por cliente
- Busca por nome, CPF ou telefone
- Total de clientes ativos

**Vendas:**
- Listar por período
- Buscar venda específica com itens
- Cancelar venda (devolve estoque)
- Total de vendas por período

**Estoque:**
- Histórico de movimentações
- Movimentações por produto
- Entradas e saídas separadas

## 🔄 Histórico de Versões

### v1.6.0 (Atual)
- Sistema completo de cadastro de clientes
- Relacionamento clientes-vendas
- Histórico de compras por cliente
- Cadastro rápido durante vendas

### v1.5.0
- Estrutura de vendas completa
- Tabelas vendas e itens_venda
- Sistema de PDV funcional

### v1.4.0
- Busca em tempo real
- Filtros avançados (tamanho, cor, preço, estoque baixo)
- Ordenação clicável nas colunas

### v1.3.0
- Filtros de pesquisa
- Sistema de paginação

### v1.2.0
- Paginação na listagem de produtos

## 🛠️ Manutenção e Troubleshooting

### Problemas Comuns

**Banco de dados não inicializa:**
- Verifique se o arquivo `init_db.sql` existe em `banco/`
- Verifique permissões de escrita na pasta de dados

**Erro ao finalizar venda:**
- Verifique estoque disponível
- Confirme que os produtos estão ativos
- Verifique conexão com o banco

**Busca não retorna resultados:**
- Verifique se há produtos cadastrados
- Confirme que produtos estão ativos
- Limpe os filtros e tente novamente

### Backup do Banco de Dados

**Windows:**
```
Copie: %LOCALAPPDATA%\EstoqueLoja\estoque.db
```

**Linux/Mac:**
```bash
cp ~/.local/share/estoque_loja/estoque.db ~/backup_estoque.db
```

## 📝 Licença e Contribuições

Este é um projeto open source. Contribuições são bem-vindas!

**Repositório:** https://github.com/FrankSCarvalho/sistema_pdv

## 👨‍💻 Desenvolvedor

Desenvolvido para atender necessidades reais de pequenos e médios varejistas do setor de vestuário.

## 🔮 Roadmap Futuro

- [ ] Módulo de relatórios gráficos
- [ ] Exportação de dados (Excel, PDF)
- [ ] Sistema de usuários e permissões
- [ ] Impressão de cupom fiscal
- [ ] Dashboard com métricas
- [ ] Backup automático
- [ ] Integração com balanças
- [ ] App mobile para consultas
- [ ] API REST para integrações

---

**Última atualização:** Janeiro 2026