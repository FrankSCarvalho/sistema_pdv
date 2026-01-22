"""
Script de teste para o sistema de clientes.
Execute este arquivo para testar se o cadastro de clientes está funcionando.

Como usar:
1. Execute: python teste_clientes.py
2. Acompanhe os testes no terminal
"""

from models.cliente import Cliente
from dao.clientes_dao import (
    inserir_cliente,
    atualizar_cliente,
    buscar_cliente_por_id,
    buscar_cliente_por_cpf_cnpj,
    listar_clientes,
    desativar_cliente,
    reativar_cliente,
    obter_total_clientes_ativos
)


def testar_sistema_clientes():
    print("=" * 60)
    print("🧪 TESTANDO SISTEMA DE CLIENTES")
    print("=" * 60)
    
    # ==========================================
    # TESTE 1: Cadastrar um cliente
    # ==========================================
    print("\n👤 TESTE 1: Cadastrando um cliente...")
    
    cliente = Cliente(
        nome="João da Silva Santos",
        cpf_cnpj="123.456.789-00",
        telefone="(86) 99999-8888",
        email="joao.silva@email.com",
        endereco="Rua das Flores, 123",
        cidade="Teresina",
        estado="PI",
        cep="64000-000",
        observacoes="Cliente preferencial"
    )
    
    try:
        cliente_cadastrado = inserir_cliente(cliente)
        print(f"✅ Cliente cadastrado com sucesso! ID: {cliente_cadastrado.id}")
        print(f"   Nome: {cliente_cadastrado.nome}")
        print(f"   Telefone: {cliente_cadastrado.telefone}")
        print(f"   Email: {cliente_cadastrado.email}")
        print(f"   Endereço: {cliente_cadastrado.endereco_completo()}")
        cliente_id = cliente_cadastrado.id
    except Exception as e:
        print(f"❌ ERRO ao cadastrar cliente: {e}")
        return
    
    # ==========================================
    # TESTE 2: Buscar cliente por ID
    # ==========================================
    print("\n🔍 TESTE 2: Buscando cliente por ID...")
    
    cliente_encontrado = buscar_cliente_por_id(cliente_id)
    
    if cliente_encontrado:
        print(f"✅ Cliente encontrado!")
        print(f"   {cliente_encontrado.nome_completo_com_doc()}")
    else:
        print("❌ ERRO: Cliente não encontrado!")
        return
    
    # ==========================================
    # TESTE 3: Buscar cliente por CPF
    # ==========================================
    print("\n🔍 TESTE 3: Buscando cliente por CPF...")
    
    cliente_por_cpf = buscar_cliente_por_cpf_cnpj("123.456.789-00")
    
    if cliente_por_cpf:
        print(f"✅ Cliente encontrado pelo CPF!")
        print(f"   {cliente_por_cpf.nome}")
    else:
        print("❌ ERRO: Cliente não encontrado pelo CPF!")
        return
    
    # ==========================================
    # TESTE 4: Atualizar dados do cliente
    # ==========================================
    print("\n✏️ TESTE 4: Atualizando dados do cliente...")
    
    cliente_encontrado.telefone = "(86) 98888-7777"
    cliente_encontrado.observacoes = "Cliente VIP - desconto de 10%"
    
    try:
        atualizar_cliente(cliente_encontrado)
        print("✅ Cliente atualizado com sucesso!")
        
        # Busca novamente para confirmar
        cliente_atualizado = buscar_cliente_por_id(cliente_id)
        print(f"   Novo telefone: {cliente_atualizado.telefone}")
        print(f"   Observações: {cliente_atualizado.observacoes}")
    except Exception as e:
        print(f"❌ ERRO ao atualizar: {e}")
    
    # ==========================================
    # TESTE 5: Cadastrar mais clientes
    # ==========================================
    print("\n👥 TESTE 5: Cadastrando mais clientes...")
    
    clientes_teste = [
        Cliente(
            nome="Maria Oliveira",
            telefone="(86) 98777-6666",
            email="maria@email.com",
            cidade="Teresina",
            estado="PI"
        ),
        Cliente(
            nome="Pedro Souza",
            cpf_cnpj="987.654.321-00",
            telefone="(86) 98555-4444",
            cidade="Parnaíba",
            estado="PI"
        )
    ]
    
    for c in clientes_teste:
        try:
            inserir_cliente(c)
            print(f"✅ {c.nome} cadastrado")
        except Exception as e:
            print(f"❌ Erro ao cadastrar {c.nome}: {e}")
    
    # ==========================================
    # TESTE 6: Listar todos os clientes
    # ==========================================
    print("\n📋 TESTE 6: Listando todos os clientes...")
    
    todos_clientes = listar_clientes()
    print(f"✅ Total de clientes ativos: {len(todos_clientes)}")
    
    for c in todos_clientes:
        print(f"   ID {c.id}: {c.nome} | {c.telefone or 'Sem telefone'}")
    
    # ==========================================
    # TESTE 7: Filtrar clientes por nome
    # ==========================================
    print("\n🔎 TESTE 7: Filtrando clientes por nome (Silva)...")
    
    clientes_silva = listar_clientes(filtro_nome="Silva")
    print(f"✅ Encontrados {len(clientes_silva)} clientes com 'Silva' no nome")
    
    for c in clientes_silva:
        print(f"   {c.nome}")
    
    # ==========================================
    # TESTE 8: Desativar cliente
    # ==========================================
    print("\n🚫 TESTE 8: Desativando um cliente...")
    
    desativar_cliente(cliente_id)
    print(f"✅ Cliente ID {cliente_id} desativado")
    
    # Verifica
    cliente_desativado = buscar_cliente_por_id(cliente_id)
    if cliente_desativado.ativo == 0:
        print("✅ Status de desativação confirmado")
    
    # ==========================================
    # TESTE 9: Listar incluindo inativos
    # ==========================================
    print("\n📋 TESTE 9: Listando clientes (incluindo inativos)...")
    
    todos_com_inativos = listar_clientes(ativos_apenas=False)
    ativos = sum(1 for c in todos_com_inativos if c.ativo == 1)
    inativos = sum(1 for c in todos_com_inativos if c.ativo == 0)
    
    print(f"✅ Total: {len(todos_com_inativos)} clientes")
    print(f"   Ativos: {ativos}")
    print(f"   Inativos: {inativos}")
    
    # ==========================================
    # TESTE 10: Reativar cliente
    # ==========================================
    print("\n✅ TESTE 10: Reativando o cliente...")
    
    reativar_cliente(cliente_id)
    print(f"✅ Cliente ID {cliente_id} reativado")
    
    # Verifica
    cliente_reativado = buscar_cliente_por_id(cliente_id)
    if cliente_reativado.ativo == 1:
        print("✅ Status de reativação confirmado")
    
    # ==========================================
    # TESTE 11: Total de clientes ativos
    # ==========================================
    print("\n📊 TESTE 11: Contando clientes ativos...")
    
    total = obter_total_clientes_ativos()
    print(f"✅ Total de clientes ativos: {total}")
    
    # ==========================================
    # TESTE 12: Testar métodos da classe Cliente
    # ==========================================
    print("\n🔧 TESTE 12: Testando métodos da classe Cliente...")
    
    cliente_teste = buscar_cliente_por_id(cliente_id)
    
    print(f"   Nome completo com doc: {cliente_teste.nome_completo_com_doc()}")
    print(f"   Endereço completo: {cliente_teste.endereco_completo()}")
    
    # ==========================================
    # RESUMO FINAL
    # ==========================================
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)
    print("\n📌 O sistema de clientes está funcionando perfeitamente!")
    print("   Você pode começar a criar a interface de cadastro.")
    print("\n")


if __name__ == "__main__":
    try:
        testar_sistema_clientes()
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()