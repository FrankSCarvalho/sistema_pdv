-- ============================================
-- SISTEMA DE CONTROLE DE ESTOQUE - LOJA DE ROUPAS
-- Versão: 1.6.0
-- ============================================

PRAGMA foreign_keys = ON;

-- =========================
-- TABELA: clientes
-- Cadastro de clientes da loja
-- =========================

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,                          -- Nome completo do cliente
    cpf_cnpj TEXT UNIQUE,                        -- CPF ou CNPJ (opcional)
    telefone TEXT,                               -- Telefone para contato
    email TEXT,                                  -- Email do cliente
    endereco TEXT,                               -- Endereço completo
    cidade TEXT,                                 -- Cidade
    estado TEXT,                                 -- UF (ex: PI, SP)
    cep TEXT,                                    -- CEP
    observacoes TEXT,                            -- Observações sobre o cliente
    data_cadastro TEXT NOT NULL,                 -- Data do cadastro
    ativo INTEGER NOT NULL DEFAULT 1             -- 0 = inativo, 1 = ativo
);

-- =========================
-- ÍNDICES DA TABELA clientes
-- =========================

CREATE INDEX IF NOT EXISTS idx_clientes_nome
ON clientes(nome);

CREATE INDEX IF NOT EXISTS idx_clientes_cpf_cnpj
ON clientes(cpf_cnpj);

CREATE INDEX IF NOT EXISTS idx_clientes_telefone
ON clientes(telefone);

-- =========================
-- TABELA: produtos
-- =========================

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_barras TEXT UNIQUE,
    nome TEXT NOT NULL,
    categoria TEXT,
    tamanho TEXT,
    cor TEXT,
    preco_custo REAL,
    preco_venda REAL NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1
);

-- =========================
-- ÍNDICES DA TABELA produtos
-- =========================

CREATE INDEX IF NOT EXISTS idx_produtos_codigo_barras
ON produtos(codigo_barras);

CREATE INDEX IF NOT EXISTS idx_produtos_nome
ON produtos(nome);

-- =========================
-- TABELA: movimentacoes_estoque
-- =========================

CREATE TABLE IF NOT EXISTS movimentacoes_estoque(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data TEXT NOT NULL,
    observacao TEXT,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- =========================
-- ÍNDICES DA TABELA movimentacoes_estoque
-- =========================

CREATE INDEX IF NOT EXISTS idx_mov_estoque_produto
ON movimentacoes_estoque(produto_id);

CREATE INDEX IF NOT EXISTS idx_mov_estoque_data
ON movimentacoes_estoque(data);

-- =========================
-- TABELA: vendas
-- Armazena informações gerais de cada venda
-- =========================

CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,                          -- Data e hora da venda
    total REAL NOT NULL CHECK (total >= 0),      -- Valor total da venda
    desconto REAL DEFAULT 0 CHECK (desconto >= 0), -- Desconto aplicado
    forma_pagamento TEXT NOT NULL,               -- Ex: DINHEIRO, PIX, CARTAO_DEBITO, CARTAO_CREDITO
    observacao TEXT,                             -- Observações opcionais
    cliente_id INTEGER DEFAULT NULL,             -- Cliente que fez a compra (opcional)
    usuario_id INTEGER DEFAULT NULL,             -- Vendedor (NULL por enquanto, depois usaremos)
    cancelada INTEGER NOT NULL DEFAULT 0,        -- 0 = ativa, 1 = cancelada
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- =========================
-- TABELA: itens_venda
-- Armazena cada produto vendido em uma venda
-- =========================

CREATE TABLE IF NOT EXISTS itens_venda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,                   -- Qual venda pertence este item
    produto_id INTEGER NOT NULL,                 -- Qual produto foi vendido
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),  -- Quantidade vendida
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0), -- Preço no momento da venda
    subtotal REAL NOT NULL CHECK (subtotal >= 0), -- quantidade × preco_unitario
    FOREIGN KEY (venda_id) REFERENCES vendas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- =========================
-- ÍNDICES DAS TABELAS DE VENDAS
-- =========================

CREATE INDEX IF NOT EXISTS idx_vendas_data
ON vendas(data);

CREATE INDEX IF NOT EXISTS idx_vendas_cliente_id
ON vendas(cliente_id);

CREATE INDEX IF NOT EXISTS idx_itens_venda_venda_id
ON itens_venda(venda_id);

CREATE INDEX IF NOT EXISTS idx_itens_venda_produto_id
ON itens_venda(produto_id);