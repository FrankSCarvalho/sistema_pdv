-- ============================================
-- SISTEMA DE CONTROLE DE ESTOQUE - LOJA DE ROUPAS
-- Versão: 1.0
-- ============================================

PRAGMA foreign_keys = ON;

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