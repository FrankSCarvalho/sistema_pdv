# Implementação do Sistema de Login

## 📋 Visão Geral

Este documento explica como implementar o sistema de login com níveis de acesso no Sistema PDV.

## 🎯 Níveis de Acesso

### 1. **Administrador** (Nível 1)
- ✅ Acesso total ao sistema
- ✅ Gerenciar produtos (cadastrar, editar, desativar)
- ✅ Gerenciar clientes
- ✅ Realizar vendas (PDV)
- ✅ Movimentação de estoque
- ✅ Gerenciar usuários (criar, editar, desativar)
- ✅ Cancelar vendas

### 2. **Gerente** (Nível 2)
- ✅ Gerenciar produtos (cadastrar, editar)
- ✅ Gerenciar clientes
- ✅ Realizar vendas (PDV)
- ✅ Cancelar vendas
- ❌ Movimentação de estoque
- ❌ Gerenciar usuários

### 3. **Vendedor** (Nível 3)
- ✅ Realizar vendas (PDV)
- ✅ Consultar produtos (somente leitura)
- ❌ Cadastrar/editar produtos
- ❌ Gerenciar clientes
- ❌ Movimentação de estoque
- ❌ Cancelar vendas
- ❌ Gerenciar usuários

## 🚀 Passo a Passo da Implementação

### Passo 1: Backup do Banco de Dados

**IMPORTANTE:** Faça backup do seu banco de dados antes de continuar!

**Windows:**
```cmd
copy "%LOCALAPPDATA%\EstoqueLoja\estoque.db" "%LOCALAPPDATA%\EstoqueLoja\estoque_backup.db"
```

**Linux/Mac:**
```bash
cp ~/.local/share/estoque_loja/estoque.db ~/.local/share/estoque_loja/estoque_backup.db
```

### Passo 2: Copiar os Novos Arquivos

Copie os seguintes arquivos para o diretório do seu projeto:

**Novos arquivos de modelo:**
- `modelos/usuario.py`

**Novos arquivos DAO:**
- `dao/usuarios_dao.py`

**Novas telas:**
- `telas/tela_login.py`
- `telas/tela_usuarios.py`

**Arquivos atualizados:**
- `main_com_login.py` (novo ponto de entrada)
- `tela_principal_com_login.py` (versão com controle de acesso)
- `init_db_updated.sql` (nova estrutura do banco)

**Script de migração:**
- `migrar_banco.py`

### Passo 3: Executar a Migração do Banco

Execute o script de migração para adicionar a tabela de usuários:

```bash
python migrar_banco.py
```

O script irá:
1. Criar backup automático do banco
2. Criar a tabela `usuarios`
3. Adicionar coluna `usuario_id` nas tabelas `vendas` e `movimentacoes_estoque`
4. Criar usuário administrador padrão:
   - **Login:** admin
   - **Senha:** admin123

### Passo 4: Atualizar o Arquivo Principal

Renomeie ou substitua o arquivo `main.py`:

```bash
# Backup do main.py original
mv main.py main_sem_login.py

# Use o novo main com login
cp main_com_login.py main.py
```

Ou simplesmente execute diretamente:
```bash
python main_com_login.py
```

### Passo 5: Atualizar a Tela Principal

Substitua `telas/tela_principal.py` por `tela_principal_com_login.py`:

```bash
mv telas/tela_principal.py telas/tela_principal_sem_login.py
cp tela_principal_com_login.py telas/tela_principal.py
```

### Passo 6: Primeiro Login

1. Execute o sistema:
```bash
python main.py
```

2. Faça login com as credenciais padrão:
   - **Usuário:** admin
   - **Senha:** admin123

3. **IMPORTANTE:** Altere a senha do administrador imediatamente:
   - Acesse "👥 Gerenciar Usuários"
   - Selecione o usuário "Administrador"
   - Clique em "🔑 Alterar Senha"
   - Digite uma senha segura

### Passo 7: Criar Usuários para sua Equipe

1. Acesse "👥 Gerenciar Usuários"
2. Preencha os dados:
   - Nome completo
   - Login (nome de usuário único)
   - Senha (mínimo 6 caracteres)
   - Nível de acesso
3. Clique em "💾 Salvar Novo"

## 🔧 Estrutura do Banco de Dados

### Nova Tabela: `usuarios`

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    nivel_acesso INTEGER NOT NULL DEFAULT 3,
    ativo INTEGER NOT NULL DEFAULT 1,
    data_criacao TEXT NOT NULL,
    ultimo_acesso TEXT
);
```

### Colunas Adicionadas

**Tabela `vendas`:**
- `usuario_id INTEGER` - ID do vendedor que realizou a venda

**Tabela `movimentacoes_estoque`:**
- `usuario_id INTEGER` - ID do usuário que fez a movimentação

## 📝 Uso do Sistema

### Login

1. Ao iniciar o sistema, a tela de login será exibida
2. Digite seu usuário e senha
3. Clique em "ENTRAR"
4. O sistema abrirá a tela principal com os módulos disponíveis para seu nível de acesso

### Gerenciamento de Usuários (Apenas Administradores)

**Criar Novo Usuário:**
1. Acesse "👥 Gerenciar Usuários"
2. Preencha os campos obrigatórios
3. Selecione o nível de acesso
4. Clique em "💾 Salvar Novo"

**Editar Usuário:**
1. Selecione o usuário na lista
2. Altere os dados necessários
3. Clique em "✏️ Atualizar"

**Alterar Senha:**
1. Selecione o usuário
2. Clique em "🔑 Alterar Senha"
3. Digite a nova senha duas vezes
4. Clique em "✅ Salvar"

**Desativar/Reativar Usuário:**
1. Selecione o usuário
2. Clique em "❌ Desativar" ou "✅ Reativar"

## 🔐 Segurança

### Senhas

- As senhas são armazenadas como hash SHA-256
- Nunca são armazenadas em texto plano
- Mínimo de 6 caracteres obrigatório

### Controle de Acesso

- Cada tela verifica as permissões do usuário logado
- Botões são ocultados se o usuário não tem permissão
- Tentativas de acesso não autorizado são bloqueadas

### Auditoria

- Data de criação de cada usuário é registrada
- Último acesso é atualizado a cada login
- Vendas e movimentações de estoque registram qual usuário executou a ação

## 🛠️ Troubleshooting

### Erro: "Tabela usuarios já existe"

Se você executar o script de migração mais de uma vez, verá esta mensagem. Isso é normal e significa que a migração já foi realizada.

### Esqueci a senha do administrador

Se você esqueceu a senha do administrador, você pode:

1. **Opção 1:** Usar um editor SQLite para redefinir a senha:
```sql
UPDATE usuarios 
SET senha_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
WHERE login = 'admin';
-- Esta é a senha: admin123
```

2. **Opção 2:** Restaurar o backup do banco de dados e executar a migração novamente

### Erro ao fazer login

- Verifique se o usuário está ativo
- Confirme que está digitando a senha corretamente
- Verifique se a migração do banco foi executada com sucesso

### Usuário não consegue acessar um módulo

- Verifique o nível de acesso do usuário
- Consulte a tabela de permissões no início deste documento
- Apenas administradores podem alterar níveis de acesso

## 📊 Relatório de Alterações

### Versão 2.0.0

**Novos Recursos:**
- ✅ Sistema de login com autenticação
- ✅ Três níveis de acesso (Admin, Gerente, Vendedor)
- ✅ Gerenciamento de usuários
- ✅ Controle de permissões por tela
- ✅ Registro de usuário em vendas e movimentações
- ✅ Auditoria de acessos

**Arquivos Novos:**
- `modelos/usuario.py`
- `dao/usuarios_dao.py`
- `telas/tela_login.py`
- `telas/tela_usuarios.py`
- `migrar_banco.py`

**Arquivos Modificados:**
- `main.py` → `main_com_login.py`
- `telas/tela_principal.py` → `tela_principal_com_login.py`
- `banco/init_db.sql` → `init_db_updated.sql`

**Banco de Dados:**
- Nova tabela: `usuarios`
- Nova coluna em `vendas`: `usuario_id`
- Nova coluna em `movimentacoes_estoque`: `usuario_id`
- Novos índices para otimização

## 📞 Suporte

Se encontrar problemas durante a implementação:

1. Verifique se todos os arquivos foram copiados corretamente
2. Confirme que o backup do banco foi feito
3. Revise as mensagens de erro do script de migração
4. Consulte a documentação técnica em `ARCHITECTURE.md`

## ✅ Checklist de Implementação

- [ ] Backup do banco de dados realizado
- [ ] Novos arquivos copiados para o projeto
- [ ] Script de migração executado com sucesso
- [ ] Primeiro login realizado (admin/admin123)
- [ ] Senha do administrador alterada
- [ ] Usuários da equipe criados
- [ ] Níveis de acesso configurados
- [ ] Testes de permissões realizados
- [ ] Sistema funcionando corretamente

---

**Versão do Documento:** 1.0  
**Data:** Janeiro 2026  
**Autor:** Sistema PDV Team
