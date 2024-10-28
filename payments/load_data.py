import os
import sys
import django
import numpy as np
import pandas as pd
from datetime import datetime

# Get the absolute path to the directory containing this file (run_select.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the project root directory (three levels up from the current directory)
project_root = os.path.dirname(current_dir)

# Add the project root to the Python path
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')  # Substitua 'nomedoprojeto' pelo nome correto

# Initialize Django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from clients.models import Clients
from adquirentes.models import Acquirer
from payments.models import Received, Product, TransactionType, Bank, Modality, PaymentStatus

def handle_products(products_df, new_df):
    # Converte a coluna 'code' para string para garantir a comparação correta
    new_df['code'] = new_df['code'].astype(str)
    products_df['code'] = products_df['code'].astype(str)

    # Encontra os códigos que estão em 'products' mas não em 'products_df'
    codes_to_add = new_df[~new_df['code'].isin(products_df['code'])]

    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo Product
        new_product = Product(
            code=row['code'],      # Substitua pelo nome correto da coluna se necessário
            name=row['name']       # Certifique-se de que 'name' exista no DataFrame 'products'
        )
        new_product.save()  # Salva a nova instância no banco de dados

    print(f"Total de produtos cadastrados: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        products_df = pd.DataFrame(list(Product.objects.all().values()))

    # Se o product_id for igual a 0, então ele assume o valor da coluna id    
    products_df.loc[products_df['product_id'] == 0, 'product_id'] = products_df['id']
    
    return products_df
    
def handle_transactions(transaction_types_df, new_df):
    codes_to_add = new_df[~new_df['id'].isin(transaction_types_df['id'])]
    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo TransactionType
        new_transaction = TransactionType(
            id=row['id'],      # Substitua pelo nome correto da coluna se necessário
            name=row['name']       # Certifique-se de que 'name' exista no DataFrame 'products'
        )
        new_transaction.save()  # Salva a nova instância no banco de dados

    print(f"Total de transactions cadastradss: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        transaction_types_df = pd.DataFrame(list(TransactionType.objects.all().values()))
    
    return transaction_types_df

def handle_modalities(modalities_df, new_df):
    new_df['id'] = new_df['id'].astype(str)
    modalities_df['code'] = modalities_df['code'].astype(str)    
    codes_to_add = new_df[~new_df['id'].isin(modalities_df['code'])]
    
    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo TransactionType
        new_modality = Modality(
            code=row['id'],      # Substitua pelo nome correto da coluna se necessário
            name=row['name']       # Certifique-se de que 'name' exista no DataFrame 'products'
        )
        new_modality.save()  # Salva a nova instância no banco de dados

    print(f"Total de modalidades cadastradss: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        modalities_df = pd.DataFrame(list(Modality.objects.all().values()))
    
    return modalities_df

def handle_payment_status(payment_status_df, new_df):
    payment_status_df['code'] = payment_status_df['code'].astype(float)
    payment_status['id'] = payment_status['id'].where(payment_status['id'].notna(), None)

    codes_to_add = new_df[~new_df['id'].isin(payment_status_df['code'])]
    
    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo TransactionType
        new_status_payment = PaymentStatus(
            code=row['id'],      # Substitua pelo nome correto da coluna se necessário
            description=row['description']       # Certifique-se de que 'name' exista no DataFrame 'products'
        )
        new_status_payment.save()  # Salva a nova instância no banco de dados

    print(f"Total de new_status_payment cadastradss: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        payment_status_df = pd.DataFrame(list(PaymentStatus.objects.all().values()))
    
    return payment_status_df

def handle_acquires(adquirentes_df, new_df):
    codes_to_add = new_df[~new_df['id'].isin(adquirentes_df['id'])]

    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo TransactionType
        new_adquirente = Acquirer(
            id=row['id'],      # Substitua pelo nome correto da coluna se necessário
            name=row['name']       # Certifique-se de que 'name' exista no DataFrame 'products'
        )
        new_adquirente.save()  # Salva a nova instância no banco de dados

    print(f"Total de new_adquirente cadastradss: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        adquirentes_df = pd.DataFrame(list(Acquirer.objects.all().values()))
    
    return adquirentes_df

def handle_banks(banks_df, new_df):
    codes_to_add = new_df[~new_df['id'].isin(banks_df['id'])]

    # Itera sobre os códigos que precisam ser adicionados
    for index, row in codes_to_add.iterrows():
        # Cria uma nova instância do modelo TransactionType
        new_bank = Bank(
            id=row['id']
        )
        new_bank.save()  # Salva a nova instância no banco de dados

    print(f"Total de new_bank cadastrados: {len(codes_to_add)}")

    if len(codes_to_add) > 0:
        banks_df = pd.DataFrame(list(Bank.objects.all().values()))
    
    return banks_df


# 1. Carregue o CSV utilizando pandas
csv_file_path = os.path.join(current_dir, 'campeao_data.csv')
# Lê o arquivo CSV e armazena em um DataFrame, removendo espaços em branco
# csv_df = pd.read_csv(csv_file_path, skipinitialspace=True) # Lendo na codificação UTF-8
csv_df = pd.read_csv(csv_file_path, skipinitialspace=True, encoding='latin1')

# 2. Transforme os modelos em DataFrames
clients_df = pd.DataFrame(list(Clients.objects.all().values('cnpj', 'id')))
products_query = Product.objects.all().values('id','code', 'name', 'product_id')
if products_query.exists():
    products_df = pd.DataFrame(list(products_query))
else:
    products_df = pd.DataFrame(columns=['id','code', 'name', 'product_id'])

transactions_query = TransactionType.objects.all().values('id','name')
if transactions_query.exists():
    transaction_types_df = pd.DataFrame(list(transactions_query))
else:
    transaction_types_df = pd.DataFrame(columns=['id', 'name'])

modalities_query = Modality.objects.all().values('id','name', 'code')
if modalities_query.exists():
    modalities_df = pd.DataFrame(list(modalities_query))
else:
    modalities_df = pd.DataFrame(columns=['id', 'name', 'code'])
    
payment_status_query = PaymentStatus.objects.all().values('id','description', 'code')
if payment_status_query.exists():
    payment_status_df = pd.DataFrame(list(payment_status_query))
else:
    payment_status_df = pd.DataFrame(columns=['id', 'description', 'code']) 
    
acquires_query = Acquirer.objects.all().values('id','name')
if acquires_query.exists():
    adquirentes_df = pd.DataFrame(list(acquires_query))
else:
    adquirentes_df = pd.DataFrame(columns=['id', 'name'])    
    
banks_query = Bank.objects.all().values('id','name')
if banks_query.exists():
    banks_df = pd.DataFrame(list(banks_query))
else:
    banks_df = pd.DataFrame(columns=['id', 'name'])        

# Converta ambas as colunas para string, se necessário
csv_df['Cnpj'] = csv_df['Cnpj'].astype(str)
clients_df['cnpj'] = clients_df['cnpj'].astype(str)
csv_df.rename(columns={'Cnpj': 'cnpj'}, inplace=True)
# 3. Agora, você pode cruzar os DataFrames com o CSV
# Fazer o merge entre csv_df e clients_df com base na coluna 'cnpj'
merged_df = pd.merge(csv_df, clients_df[['cnpj', 'id']], on='cnpj', how='left')

# Renomear a coluna 'id' do clients_df para 'client_id' (opcional)
merged_df = merged_df.rename(columns={'id': 'client_id'})
merged_df['CodigoProduto'] = merged_df['CodigoProduto'].astype(str)

# Tratando os produtos
products = merged_df[['CodigoProduto', 'Produto', 'client_id']].drop_duplicates()
products = products.rename(columns={'CodigoProduto': 'code', 'Produto':'name'})
products_df = handle_products(products_df, products)

# Tratando os tipos de transação
transactions = merged_df[['IdTipoTransacao', 'TipoTransacao']].drop_duplicates()
transactions = transactions.rename(columns={'IdTipoTransacao':'id', 'TipoTransacao':'name'})
transaction_types_df = handle_transactions(transaction_types_df, transactions)
transaction_types_df = transaction_types_df.rename(columns={'id':'transaction_id'})

# Tratando os bancos
banks = merged_df[['Banco']].drop_duplicates()
merged_df = merged_df.rename(columns={'Banco':'banco'})
banks = banks.rename(columns={'Banco':'id'})
banks_df = handle_banks(banks_df, banks)

# Tratando as modalidades
modalities = merged_df[['IdModalidade', 'Modalidade']].drop_duplicates()
modalities = modalities.rename(columns={'IdModalidade':'id', 'Modalidade':'name'})
modalities['id'] = modalities['id'].where(modalities['id'].notna(), None)
modalities_df = handle_modalities(modalities_df, modalities)
modalities_df = modalities_df.rename(columns={'id':'modality_id'})
merged_df['IdModalidade'] = merged_df['IdModalidade'].astype(str)
modalities_df['code'] = modalities_df['code'].astype(str)    

# Tratando os Status de Pagamento
payment_status = merged_df[['IdStatus', 'Status']].drop_duplicates()
payment_status = payment_status.rename(columns={'IdStatus':'id', 'Status':'description'})
payment_status['id'] = payment_status['id'].where(payment_status['id'].notna(), None)
payment_status_df = handle_payment_status(payment_status_df, payment_status)
payment_status_df = payment_status_df.rename(columns={'id':'payment_status_id'})

# Tratando os Adquirentes
acquires = merged_df[['AdqId', 'Adquirente']].drop_duplicates()
acquires = acquires.rename(columns={'AdqId':'id', 'Adquirente':'name'})
adquirentes_df = handle_acquires(adquirentes_df, acquires)
adquirentes_df = adquirentes_df.rename(columns={'id':'adquirente_id'})


# corrigindo o MERGED_DF com os products id/code
merged_df = pd.merge(merged_df, products_df[['code', 'product_id']], left_on='CodigoProduto', right_on='code', how='left') 
merged_df = pd.merge(merged_df, transaction_types_df[['transaction_id']], left_on='IdTipoTransacao', right_on='transaction_id', how='left')
merged_df = pd.merge(merged_df, modalities_df[['code', 'modality_id']], left_on='IdModalidade', right_on='code', how='left')
merged_df = pd.merge(merged_df, payment_status_df[['code', 'payment_status_id']], left_on='IdStatus', right_on='code', how='left')
merged_df = pd.merge(merged_df, adquirentes_df[['adquirente_id']], left_on='AdqId', right_on='adquirente_id', how='left')

# Exibir valores únicos da coluna 'payment_status_id'
unique_values = merged_df['modality_id'].unique()
print('Modalidas unicas:', unique_values)


# Função para converter os valores do CSV para o modelo Django
def carregar_dados():
    # merged_df.info()   
    for index, row in merged_df.iterrows():
        try:
            # Tente buscar a instância do cliente com base no client_id
            client_instance = Clients.objects.get(id=row['client_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"Cliente com ID {row['client_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado
        
        try:
            # Tente buscar a instância do adquirente com base no id
            adquirente_instance = Acquirer.objects.get(id=row['adquirente_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"Adquirente com ID {row['adquirente_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado  
        
        try:
            # Tente buscar a instância do produto com base no id
            product_instance = Product.objects.get(id=row['product_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"Produto com ID {row['product_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado  
        
        try:
            # Tente buscar a instância do produto com base no id
            banco_instance = Bank.objects.get(id=row['banco'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"Bank com ID {row['banco']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado   
        
        try:
            # Tente buscar a instância do produto com base no id
            transaction_instance = TransactionType.objects.get(id=row['transaction_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"TransactionType com ID {row['transaction_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado                               

        try:
            # Tente buscar a instância do produto com base no id
            payment_instance = PaymentStatus.objects.get(id=row['payment_status_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"PaymentStatus com ID {row['payment_status_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado 
        
        try:
            # Tente buscar a instância do produto com base no id
            modality_instance = Modality.objects.get(id=row['modality_id'])
        except ObjectDoesNotExist:
            # Trate o caso onde o cliente não existe, se necessário
            print(f"Modality com ID {row['modality_id']} não encontrado.")
            continue  # Pula para o próximo loop se o cliente não for encontrado 
        
        # Verificação e conversão de valores
        autorizacao = str(row['Autorizacao']) if not pd.isna(row['Autorizacao']) else ''
        nsu = str(int(row['Nsu'])) if not pd.isna(row['Nsu']) else ''  # Convertendo de float para inteiro e depois para string
        id_transacao = str(row['Tid']) if not pd.isna(row['Tid']) else ''
        resumo_venda = str(row['ResumoVenda']) if not pd.isna(row['ResumoVenda']) else ''
        outras_despesas = row['OutrasDespesas'] if not pd.isna(row['OutrasDespesas']) else 0
        nome_loja = str(row['NomeLoja']) if not pd.isna(row['NomeLoja']) else ''
        divergencias = str(row['Divergencias']) if not pd.isna(row['Divergencias']) else ''
        observacao = str(row['Observacao']) if not pd.isna(row['Observacao']) else ''
        motivo_ajuste = str(row['MotivoAjuste']) if not pd.isna(row['MotivoAjuste']) else ''
        
        # Convertendo as datas do DataFrame para o formato desejado
        data_pagamento = datetime.strptime(str(row['DataPagamento']), '%Y-%m-%d') if pd.notna(row['DataPagamento']) else None
        data_prevista_pagamento = datetime.strptime(str(row['DataPrevistaPagamento']), '%Y-%m-%d') if pd.notna(row['DataPrevistaPagamento']) else None
        data_venda = datetime.strptime(str(row['DataVenda']), '%Y-%m-%d') if pd.notna(row['DataVenda']) else None        
                               
               
        try:
            # Salvando o pagamento
            pagamento = Received(
                id=row['Id'],
                id_pagamento=row['IdPagamento'],
                refo_id=row['RefoId'],
                client=client_instance,
                estabelecimento=row['Estabelecimento'],
                data_pagamento=data_pagamento,
                data_prevista_pagamento=data_prevista_pagamento,
                data_venda=data_venda,
                adquirente=adquirente_instance,
                autorizacao=autorizacao,
                nsu=nsu,
                id_transacao=id_transacao,
                parcela=row['Parcela'] if str(row['Parcela']).isdigit() else 0,
                total_parcelas = row['TotalParcelas'] if str(row['TotalParcelas']).isdigit() else 0,
                product=product_instance,
                resumo_venda=resumo_venda,
                valor_bruto=row['ValorBruto'],
                taxa=row['Taxa'] if not pd.isna(row['Taxa']) else None,
                outras_despesas=outras_despesas,
                valor_liquido=row['ValorLiquido'] if not pd.isna(row['ValorLiquido']) else None,
                idt_antecipacao=row['IdtAntecipacao'],
                banco=banco_instance,
                agencia=str(row['Agencia']) if not pd.isna(row['Agencia']) else '',
                conta=str(row['Conta']) if not pd.isna(row['Conta']) else '',
                nome_loja=nome_loja,
                terminal=row['Terminal'],
                transactiontype=transaction_instance,
                id_status=payment_instance,
                divergencias=divergencias,
                valor_liquido_venda=row['ValorLiquidoVenda'] if not pd.isna(row['ValorLiquidoVenda']) else None,
                observacao=observacao,
                motivo_ajuste=motivo_ajuste,
                conta_adquirente=False if pd.isna(row['ContaAdquirente']) or row['ContaAdquirente'] == '' else True,
                taxa_antecipacao=row['TaxaAntecipacao'] if not pd.isna(row['TaxaAntecipacao']) else None,
                taxa_antecipacao_mensal=row['TaxaAntecipacaoMensal'] if not pd.isna(row['TaxaAntecipacaoMensal']) else None,
                valor_taxa_antecipacao=row['ValorTaxaAntecipacao'] if not pd.isna(row['ValorTaxaAntecipacao']) else None,
                valor_taxa=row['ValorTaxa'] if not pd.isna(row['ValorTaxa']) else None,
                modality=modality_instance,
                tem_conciliacao_bancaria=True if row['TemConciliacaoBancaria'] == 'Sim' else False,
                cartao=row['Cartao']
            )
            
            pagamento.save()
            
        except Exception as e:
            print(f"Erro ao salvar o pagamento no índice {index}, ID {row['Id']} {row['DataPagamento']} {row['DataPrevistaPagamento']} {row['DataVenda']}: {str(e)}")
            # Imprime todas as variáveis e seus valores que estão sendo salvos
            print("Valores de pagamento que causaram o erro:")
            print(vars(pagamento))
            
            # Parar o loop após o primeiro erro
            # break            
            continue

# Chamar a função para carregar os dados
carregar_dados()
