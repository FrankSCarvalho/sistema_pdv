"""
Script de teste para o sistema de vendas.
Execute este arquivo para testar se as vendas estão funcionando corretamente.

Como usar:
1. Certifique-se de ter produtos cadastrados no sistema
2. Execute: python teste_vendas.py
3. Acompanhe os testes no terminal
"""

from models.venda import Venda, ItemVenda
from dao.vendas_dao import (
    registrar_venda,
    buscar_venda_por_id,
    listar_vendas,
    cancelar_venda,
    obter_total_vendas_periodo
)
from dao.produtos_dao import listar_produtos
from dao.clientes_dao import inserir_cliente
from models.cliente import Cliente
from datetime import date


def testar_sistema_vendas():
    print("=" * 60)
    print("🧪 TESTANDO SISTEMA DE VENDAS")
    print("=" * 60)
    
    # ==========================================
    # TESTE 1: Verificar se há produtos
    # ==========================================
    print("\n📦 TESTE 1: Verificando produtos disponíveis...")
    produtos = listar_produtos(ativos_apenas=True)
    
    if not produtos:
        print("❌ ERRO: Você precisa cadastrar produtos primeiro!")
        print("   Abra o sistema e cadastre alguns produtos antes de testar vendas.")
        return
    
    print(f"✅ Encontrados {len(produtos)} produtos ativos")
    print("\nPrimeiros 5 produtos:")
    for p in produtos[:5]:
        print(f"   ID: {p.id} | {p.nome} | Estoque: {p.estoque} | R$ {p.preco_venda:.2f}")
    
    # ==========================================
    # TESTE 2: Criar um cliente de teste
    # ==========================================
    print("\n👤 TESTE 2: Cadastrando um cliente de teste...")
    
    cliente = Cliente(
        nome="Cliente Teste da Venda",
        telefone="(86) 99999-9999",
        email="cliente.teste@email.com"
    )
    
    try:
        cliente_cadastrado = inserir_cliente(cliente)
        cliente_id_teste = cliente_cadastrado.id
        print(f"✅ Cliente cadastrado! ID: {cliente_id_teste}")
        print(f"   Nome: {cliente_cadastrado.nome}")
    except Exception as e:
        print(f"❌ ERRO ao cadastrar cliente: {e}")
        cliente_id_teste = None  # Continua sem cliente
    
    # ==========================================
    # TESTE 3: Criar uma venda
    # ==========================================
    print("\n💰 TESTE 3: Registrando uma venda de teste...")
    
    # Pega os 2 primeiros produtos que tenham estoque
    produtos_para_vender = [p for p in produtos if p.estoque > 0][:2]
    
    if not produtos_para_vender:
        print("❌ ERRO: Nenhum produto tem estoque disponível!")
        return
    
    # Cria a venda (com cliente, se foi cadastrado)
    venda = Venda(
        forma_pagamento="DINHEIRO",
        desconto=0.0,
        observacao="Venda de teste criada automaticamente",
        cliente_id=cliente_id_teste  # Vincula ao cliente
    )
    
    # Adiciona itens à venda
    total = 0.0
    for produto in produtos_para_vender:
        quantidade = 1  # Vende 1 unidade de cada
        subtotal = quantidade * produto.preco_venda
        total += subtotal
        
        item = ItemVenda(
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco_venda,
            subtotal=subtotal
        )
        venda.itens.append(item)
        
        print(f"   Adicionado: {produto.nome} | {quantidade}x R$ {produto.preco_venda:.2f} = R$ {subtotal:.2f}")
    
    venda.total = total
    print(f"\n   TOTAL DA VENDA: R$ {total:.2f}")
    if cliente_id_teste:
        print(f"   Cliente vinculado: ID {cliente_id_teste}")
    
    # Registra a venda
    try:
        venda_id = registrar_venda(venda)
        print(f"\n✅ Venda registrada com sucesso! ID: {venda_id}")
    except Exception as e:
        print(f"\n❌ ERRO ao registrar venda: {e}")
        return
    
    # ==========================================
    # TESTE 4: Buscar a venda criada
    # ==========================================
    print("\n🔍 TESTE 4: Buscando a venda criada...")
    
    venda_encontrada = buscar_venda_por_id(venda_id)
    
    if venda_encontrada:
        print(f"✅ Venda encontrada!")
        print(f"   ID: {venda_encontrada.id}")
        print(f"   Data: {venda_encontrada.data}")
        print(f"   Total: R$ {venda_encontrada.total:.2f}")
        print(f"   Forma Pagamento: {venda_encontrada.forma_pagamento}")
        print(f"   Itens: {len(venda_encontrada.itens)}")
        
        print("\n   Detalhes dos itens:")
        for item in venda_encontrada.itens:
            print(f"   - {item.produto_nome} | {item.quantidade}x R$ {item.preco_unitario:.2f} = R$ {item.subtotal:.2f}")
    else:
        print("❌ ERRO: Venda não encontrada!")
        return
    
    # ==========================================
    # TESTE 5: Listar vendas de hoje
    # ==========================================
    print("\n📋 TESTE 5: Listando vendas de hoje...")
    
    hoje = date.today().strftime("%Y-%m-%d")
    vendas_hoje = listar_vendas(data_inicial=hoje, data_final=hoje)
    
    print(f"✅ Encontradas {len(vendas_hoje)} vendas hoje")
    for v in vendas_hoje[-5:]:  # Mostra as últimas 5
        print(f"   Venda #{v.id} | {v.data} | R$ {v.total:.2f} | {v.forma_pagamento}")
    
    # ==========================================
    # TESTE 6: Calcular total de vendas de hoje
    # ==========================================
    print("\n💵 TESTE 6: Calculando total de vendas de hoje...")
    
    total_hoje = obter_total_vendas_periodo(hoje, hoje)
    print(f"✅ Total vendido hoje: R$ {total_hoje:.2f}")
    
    # ==========================================
    # TESTE EXTRA: Histórico de compras do cliente
    # ==========================================
    if cliente_id_teste:
        print("\n📊 TESTE EXTRA: Histórico de compras do cliente...")
        
        historico = obter_historico_compras_cliente(cliente_id_teste)
        print(f"✅ Cliente tem {len(historico)} compra(s) registrada(s)")
        
        for h in historico:
            print(f"   Venda #{h['venda_id']} | {h['data']} | R$ {h['total']:.2f}")
        
        total_gasto = obter_total_gasto_cliente(cliente_id_teste)
        print(f"\n💰 Total gasto pelo cliente: R$ {total_gasto:.2f}")
    
    # ==========================================
    # TESTE 7: Cancelar a venda de teste
    # ==========================================
    print("\n🚫 TESTE 7: Cancelando a venda de teste...")
    
    try:
        cancelar_venda(venda_id)
        print(f"✅ Venda #{venda_id} cancelada com sucesso!")
        print("   Os produtos foram devolvidos ao estoque.")
        
        # Verifica se foi cancelada
        venda_cancelada = buscar_venda_por_id(venda_id)
        if venda_cancelada.cancelada == 1:
            print("✅ Status de cancelamento confirmado no banco")
        
    except Exception as e:
        print(f"❌ ERRO ao cancelar venda: {e}")
    
    # ==========================================
    # RESUMO FINAL
    # ==========================================
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)
    print("\n📌 Próximos passos:")
    print("   1. Revise os resultados acima")
    print("   2. Verifique se o estoque foi atualizado corretamente")
    print("   3. Agora você pode criar a interface de vendas!")
    print("\n")


if __name__ == "__main__":
    try:
        testar_sistema_vendas()
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()