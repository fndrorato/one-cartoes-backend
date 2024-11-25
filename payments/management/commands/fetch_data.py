from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
import sys
import requests
import numpy as np
import pandas as pd
from datetime import datetime, date
from adquirentes.models import Acquirer
from payments.models import Received, Product, TransactionType, Bank, Modality, PaymentStatus
from clients.models import Groups, Clients

class Command(BaseCommand):
    help = 'Coleta dados de uma API externa e armazena no banco de dados'
    
    def handle_products(self, products_df, new_df):
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
        
    def handle_transactions(self, transaction_types_df, new_df):
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

    def handle_modalities(self, modalities_df, new_df):
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

    def handle_payment_status(self, payment_status_df, new_df):
        payment_status_df['code'] = payment_status_df['code'].astype(float)

        # Verificar se existem valores NaN ou None em `payment_status_df['code']`
        is_na_status_df = False
        if payment_status_df['code'].isna().any():
            is_na_status_df = True
        #     # Remover linhas com NaN ou None em `new_df['id']` apenas se a condição acima for verdadeira
        #     new_df = new_df.dropna(subset=['id'])

        codes_to_add = new_df[~new_df['id'].isin(payment_status_df['code'])]
        
        # Itera sobre os códigos que precisam ser adicionados
        for index, row in codes_to_add.iterrows():
            # Cria uma nova instância do modelo TransactionType
            if is_na_status_df:
                if row['id']:
                    new_status_payment = PaymentStatus(
                        code=row['id'],      # Substitua pelo nome correto da coluna se necessário
                        description=row['description']       # Certifique-se de que 'name' exista no DataFrame 'products'
                    )
                    new_status_payment.save()  # Salva a nova instância no banco de dados

        print(f"Total de new_status_payment cadastradss: {len(codes_to_add)}")

        if len(codes_to_add) > 0:
            payment_status_df = pd.DataFrame(list(PaymentStatus.objects.all().values()))
        
        return payment_status_df

    def handle_acquires(self, adquirentes_df, new_df):
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

    def handle_banks(self, banks_df, new_df):
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
    

    def handle(self, *args, **kwargs):
        # Seu código de coleta de dados aqui, ou use a função `fetch_and_save_data` que definimos antes.
        url = "https://api.conciliadora.com.br/api/ConsultaPagamento"

        # groups = Groups.objects.get(pk=5)
        groups = Groups.objects.filter(pk__gte=1, pk__lte=3)
        # Iterar sobre os grupos filtrados
        for group in groups:        
            token = group.token
            imprimir = f'{group.id} - {token}'
            print(imprimir)

            params = {"$filter": "DataPagamento ge 2024-11-01 and DataPagamento le 2024-11-30"}
            headers = {"Content-Type": "application/json", "Authorization": f"{token}"}

            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json().get("value", [])
                df = pd.DataFrame(data)
                # df = df.head(10)
                
                # Verifica se o DataFrame está vazio
                if df.empty:
                    print("DataFrame vazio, pulando para o próximo grupo...")
                    continue  # Pula para o próximo grupo                

                print(len(df['Id']))
                
                # Encontra os CNPJs distintos
                cnpjs_unicos = df['Cnpj'].unique()

                # Conta o número de CNPJs distintos e lista os valores
                total_cnpjs = len(cnpjs_unicos)
                print(f"Total de CNPJs distintos: {total_cnpjs}")
                print("Lista de CNPJs distintos:", cnpjs_unicos)

                # Para a execução do script
                # sys.exit()            
                
                # 2. Transforme os modelos em DataFrames
                # clients_df = pd.DataFrame(list(Clients.objects.all().values('cnpj', 'id')))
                clients_df = pd.DataFrame(
                    list(Clients.objects.filter(group_id=group.id).values('cnpj', 'id'))
                )
                clients_df['cnpj'] = clients_df['cnpj'].str.replace(r'[./-]', '', regex=True).astype('object')

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
                df['Cnpj'] = df['Cnpj'].astype(str)
                clients_df['cnpj'] = clients_df['cnpj'].astype(str)
                df.rename(columns={'Cnpj': 'cnpj'}, inplace=True)
                # 3. Agora, você pode cruzar os DataFrames com o CSV
                # Fazer o merge entre DF e clients_df com base na coluna 'cnpj'
                merged_df = pd.merge(df, clients_df[['cnpj', 'id']], on='cnpj', how='left')
                
                # Renomear a coluna 'id' do clients_df para 'client_id' (opcional)
                merged_df = merged_df.rename(columns={'id': 'client_id'})
                merged_df['CodigoProduto'] = merged_df['CodigoProduto'].astype(str)

                # Tratando os produtos
                products = merged_df[['CodigoProduto', 'Produto', 'client_id']].drop_duplicates()
                products = products.rename(columns={'CodigoProduto': 'code', 'Produto':'name'})
                products_df = self.handle_products(products_df, products)

                # Tratando os tipos de transação
                transactions = merged_df[['IdTipoTransacao', 'TipoTransacao']].drop_duplicates()
                transactions = transactions.rename(columns={'IdTipoTransacao':'id', 'TipoTransacao':'name'})
                transaction_types_df = self.handle_transactions(transaction_types_df, transactions)
                transaction_types_df = transaction_types_df.rename(columns={'id':'transaction_id'})

                # Tratando os bancos
                banks = merged_df[['Banco']].drop_duplicates()
                merged_df = merged_df.rename(columns={'Banco':'banco'})
                banks = banks.rename(columns={'Banco':'id'})
                banks_df = self.handle_banks(banks_df, banks)

                # Tratando as modalidades
                modalities = merged_df[['IdModalidade', 'Modalidade']].drop_duplicates()
                modalities = modalities.rename(columns={'IdModalidade':'id', 'Modalidade':'name'})
                modalities['id'] = modalities['id'].where(modalities['id'].notna(), None)
                modalities_df = self.handle_modalities(modalities_df, modalities)
                modalities_df = modalities_df.rename(columns={'id':'modality_id'})
                merged_df['IdModalidade'] = merged_df['IdModalidade'].astype(str)
                modalities_df['code'] = modalities_df['code'].astype(str)    

                # Tratando os Status de Pagamento
                payment_status = merged_df[['IdStatus', 'Status']].drop_duplicates()
                payment_status = payment_status.rename(columns={'IdStatus':'id', 'Status':'description'})
                payment_status['id'] = payment_status['id'].where(payment_status['id'].notna(), None)
                payment_status_df = self.handle_payment_status(payment_status_df, payment_status)
                payment_status_df = payment_status_df.rename(columns={'id':'payment_status_id'})

                # Tratando os Adquirentes
                acquires = merged_df[['AdqId', 'Adquirente']].drop_duplicates()
                acquires = acquires.rename(columns={'AdqId':'id', 'Adquirente':'name'})
                adquirentes_df = self.handle_acquires(adquirentes_df, acquires)
                adquirentes_df = adquirentes_df.rename(columns={'id':'adquirente_id'})


                # corrigindo o MERGED_DF com os products id/code
                try:
                    # Converte ambas as colunas para string para evitar conflitos de tipo
                    merged_df['CodigoProduto'] = merged_df['CodigoProduto'].astype(str)
                    products_df['code'] = products_df['code'].astype(str)

                    # Realiza o merge dos DataFrames
                    merged_df = pd.merge(
                        merged_df,
                        products_df[['code', 'product_id']],
                        left_on='CodigoProduto',
                        right_on='code',
                        how='left'
                    )
                except ValueError as e:
                    # Caso ocorra um erro, imprime os DataFrames e a mensagem de erro
                    print("Erro ao fazer merge:", e)
                    print("merged_df:")
                    print(merged_df.head())
                    print("products_df:")
                    print(products_df.head())
                                    
                merged_df = pd.merge(merged_df, transaction_types_df[['transaction_id']], left_on='IdTipoTransacao', right_on='transaction_id', how='left')
                merged_df = pd.merge(merged_df, modalities_df[['code', 'modality_id']], left_on='IdModalidade', right_on='code', how='left')
                merged_df = pd.merge(merged_df, payment_status_df[['code', 'payment_status_id']], left_on='IdStatus', right_on='code', how='left')
                merged_df = pd.merge(merged_df, adquirentes_df[['adquirente_id']], left_on='AdqId', right_on='adquirente_id', how='left')
                
                num_linhas = len(merged_df)
                print("Número de linhas:", num_linhas)  

                # Obtenha todas as instâncias relacionadas de uma vez e armazene em dicionários
                clients = {client.id: client for client in Clients.objects.all()}
                acquirers = {acquirer.id: acquirer for acquirer in Acquirer.objects.all()}
                products = {product.id: product for product in Product.objects.all()}
                banks = {bank.id: bank for bank in Bank.objects.all()}
                transactions = {transaction.id: transaction for transaction in TransactionType.objects.all()}
                payments = {payment.id: payment for payment in PaymentStatus.objects.all()}
                modalities = {modality.id: modality for modality in Modality.objects.all()}

                # Lista para armazenar objetos `Received`
                recebidos = []
                
                # Armazena o número de linhas antes de remover duplicatas
                num_linhas_antes = len(merged_df)

                # Remove todas as duplicatas do DataFrame
                merged_df = merged_df.drop_duplicates()

                # Armazena o número de linhas após a remoção
                num_linhas_depois = len(merged_df)

                # Calcula quantas duplicatas foram removidas
                num_duplicatas_removidas = num_linhas_antes - num_linhas_depois

                print(f"Número de duplicatas removidas: {num_duplicatas_removidas}")
                
                num_linhas_antes = len(merged_df)
                # Remover duplicados com base nas colunas 'Id' e 'client_id'
                merged_df = merged_df.drop_duplicates(subset=['Id', 'client_id'], keep='first')
                num_linhas_depois = len(merged_df)

                # Imprimir o DataFrame após a remoção dos duplicados
                num_duplicatas_removidas = num_linhas_antes - num_linhas_depois

                print(f"Número de duplicatas removidas: {num_duplicatas_removidas}")
                
                
                
                                  

                for index, row in merged_df.iterrows():
                    try:
                        
                        # Use instâncias do dicionário em vez de fazer nova busca no banco
                        client_instance = clients.get(row['client_id'])
                        adquirente_instance = acquirers.get(row['adquirente_id'])
                        product_instance = products.get(row['product_id'])
                        banco_instance = banks.get(row['banco'])
                        transaction_instance = transactions.get(row['transaction_id'])
                        payment_instance = payments.get(row['payment_status_id'])
                        modality_instance = modalities.get(row['modality_id'])

                        if not all([client_instance]):
                            print(f"Algum relacionamento de cliente não encontrado no índice {index}: {row['client_id']}. Pulando...")
                            
                        if not all([adquirente_instance]):
                            print(f"Algum relacionamento de adquirente_instance não encontrado no índice {index}. Pulando...")
                            
                        if not all([product_instance]):
                            print(f"Algum relacionamento de product_instance não encontrado no índice {index}. Pulando...")
                            
                        if not all([transaction_instance]):
                            print(f"Algum relacionamento de transaction_instance não encontrado no índice {index}. Pulando...")                                                                                    

                        if not all([client_instance, adquirente_instance, product_instance, banco_instance, transaction_instance, payment_instance, modality_instance]):
                            print(f"Algum relacionamento não encontrado no índice {index}. Pulando...")
                            continue  # Pule se algum relacionamento não foi encontrado

                        # Preencha dados e ajuste para valores ausentes ou nulos
                        autorizacao = str(row['Autorizacao']) if not pd.isna(row['Autorizacao']) else ''                      
                        # nsu = str(int(row['Nsu'])) if not pd.isna(row['Nsu']) else ''
                        nsu = str(int(row['Nsu'])) if pd.notna(row['Nsu']) and str(row['Nsu']).isdigit() else ''
                        id_transacao = str(row['Tid']) if not pd.isna(row['Tid']) else ''
                        resumo_venda = str(row['ResumoVenda']) if not pd.isna(row['ResumoVenda']) else ''
                        outras_despesas = row['OutrasDespesas'] if not pd.isna(row['OutrasDespesas']) else 0
                        nome_loja = str(row['NomeLoja']) if not pd.isna(row['NomeLoja']) else ''
                        divergencias = str(row['Divergencias']) if not pd.isna(row['Divergencias']) else ''
                        observacao = str(row['Observacao']) if not pd.isna(row['Observacao']) else ''
                        motivo_ajuste = str(row['MotivoAjuste']) if not pd.isna(row['MotivoAjuste']) else ''
                        
                        # Conversão de datas
                        data_pagamento = datetime.strptime(str(row['DataPagamento']), '%Y-%m-%d') if pd.notna(row['DataPagamento']) else None
                        data_prevista_pagamento = datetime.strptime(str(row['DataPrevistaPagamento']), '%Y-%m-%d') if pd.notna(row['DataPrevistaPagamento']) else None
                        data_venda = datetime.strptime(str(row['DataVenda']), '%Y-%m-%d') if pd.notna(row['DataVenda']) else None

                        # Criação do objeto `Received` sem salvar ainda

                            
                        recebidos.append(Received(
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
                            total_parcelas=row['TotalParcelas'] if str(row['TotalParcelas']).isdigit() else 0,
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
                        ))

                    except Exception as e:
                        print(f"Erro ao processar índice {index}: {e}")
                        # print(f"Valores da linha com problema: {row.to_dict()}")
                        continue  # Pule para a próxima linha no loop caso ocorra um erro

                # Realizando o bulk_create em uma transação para garantir atomicidade
                try:
                    # Obter os IDs únicos dos clientes que estão sendo processados
                    clientes_processados_ids = {item.client.id for item in recebidos if item.client}  # Garantir que o cliente existe

                    # Defina as datas inicial e final
                    dt_ini = date(2024, 11, 1)  # Exemplo: 1º de outubro de 2024
                    dt_fim = date(2024, 11, 30)  # Exemplo: 31 de outubro de 2024

                    # Filtrar registros com data_pagamento dentro do intervalo
                    registros_existentes = Received.objects.filter(
                        client_id__in=clientes_processados_ids,
                        data_pagamento__range=(dt_ini, dt_fim)
                    ).values_list('id', flat=True)

                    # Filtrar o `recebidos` para remover os itens que já estão no queryset
                    recebidos_filtrados = [item for item in recebidos if item.id not in registros_existentes]
                    
                    with transaction.atomic():
                        Received.objects.bulk_create(recebidos_filtrados, batch_size=400)  # Ajuste o batch_size conforme necessário
                    self.stdout.write(self.style.SUCCESS("Dados coletados e armazenados com sucesso!"))
                except Exception as e:
                    print(f"Erro ao realizar bulk_create: {str(e)}")
            
         
            
            
            
            # self.stdout.write(self.style.SUCCESS("Dados coletados e armazenados com sucesso!"))              
            
        #     for index, row in merged_df.iterrows():
        #         try:
        #             # Tente buscar a instância do cliente com base no client_id
        #             client_instance = Clients.objects.get(id=row['client_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"Cliente com ID {row['client_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado
                
        #         try:
        #             # Tente buscar a instância do adquirente com base no id
        #             adquirente_instance = Acquirer.objects.get(id=row['adquirente_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"Adquirente com ID {row['adquirente_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado  
                
        #         try:
        #             # Tente buscar a instância do produto com base no id
        #             product_instance = Product.objects.get(id=row['product_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"Produto com ID {row['product_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado  
                
        #         try:
        #             # Tente buscar a instância do produto com base no id
        #             banco_instance = Bank.objects.get(id=row['banco'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"Bank com ID {row['banco']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado   
                
        #         try:
        #             # Tente buscar a instância do produto com base no id
        #             transaction_instance = TransactionType.objects.get(id=row['transaction_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"TransactionType com ID {row['transaction_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado                               

        #         try:
        #             # Tente buscar a instância do produto com base no id
        #             payment_instance = PaymentStatus.objects.get(id=row['payment_status_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"PaymentStatus com ID {row['payment_status_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado 
                
        #         try:
        #             # Tente buscar a instância do produto com base no id
        #             modality_instance = Modality.objects.get(id=row['modality_id'])
        #         except ObjectDoesNotExist:
        #             # Trate o caso onde o cliente não existe, se necessário
        #             print(f"Modality com ID {row['modality_id']} não encontrado.")
        #             continue  # Pula para o próximo loop se o cliente não for encontrado 
                
        #         # Verificação e conversão de valores
        #         autorizacao = str(row['Autorizacao']) if not pd.isna(row['Autorizacao']) else ''
        #         nsu = str(int(row['Nsu'])) if not pd.isna(row['Nsu']) else ''  # Convertendo de float para inteiro e depois para string
        #         id_transacao = str(row['Tid']) if not pd.isna(row['Tid']) else ''
        #         resumo_venda = str(row['ResumoVenda']) if not pd.isna(row['ResumoVenda']) else ''
        #         outras_despesas = row['OutrasDespesas'] if not pd.isna(row['OutrasDespesas']) else 0
        #         nome_loja = str(row['NomeLoja']) if not pd.isna(row['NomeLoja']) else ''
        #         divergencias = str(row['Divergencias']) if not pd.isna(row['Divergencias']) else ''
        #         observacao = str(row['Observacao']) if not pd.isna(row['Observacao']) else ''
        #         motivo_ajuste = str(row['MotivoAjuste']) if not pd.isna(row['MotivoAjuste']) else ''
                
        #         # Convertendo as datas do DataFrame para o formato desejado
        #         data_pagamento = datetime.strptime(str(row['DataPagamento']), '%Y-%m-%d') if pd.notna(row['DataPagamento']) else None
        #         data_prevista_pagamento = datetime.strptime(str(row['DataPrevistaPagamento']), '%Y-%m-%d') if pd.notna(row['DataPrevistaPagamento']) else None
        #         data_venda = datetime.strptime(str(row['DataVenda']), '%Y-%m-%d') if pd.notna(row['DataVenda']) else None        
                                    
                    
        #         try:
        #             # Salvando o pagamento
        #             pagamento = Received(
        #                 id=row['Id'],
        #                 id_pagamento=row['IdPagamento'],
        #                 refo_id=row['RefoId'],
        #                 client=client_instance,
        #                 estabelecimento=row['Estabelecimento'],
        #                 data_pagamento=data_pagamento,
        #                 data_prevista_pagamento=data_prevista_pagamento,
        #                 data_venda=data_venda,
        #                 adquirente=adquirente_instance,
        #                 autorizacao=autorizacao,
        #                 nsu=nsu,
        #                 id_transacao=id_transacao,
        #                 parcela=row['Parcela'] if str(row['Parcela']).isdigit() else 0,
        #                 total_parcelas = row['TotalParcelas'] if str(row['TotalParcelas']).isdigit() else 0,
        #                 product=product_instance,
        #                 resumo_venda=resumo_venda,
        #                 valor_bruto=row['ValorBruto'],
        #                 taxa=row['Taxa'] if not pd.isna(row['Taxa']) else None,
        #                 outras_despesas=outras_despesas,
        #                 valor_liquido=row['ValorLiquido'] if not pd.isna(row['ValorLiquido']) else None,
        #                 idt_antecipacao=row['IdtAntecipacao'],
        #                 banco=banco_instance,
        #                 agencia=str(row['Agencia']) if not pd.isna(row['Agencia']) else '',
        #                 conta=str(row['Conta']) if not pd.isna(row['Conta']) else '',
        #                 nome_loja=nome_loja,
        #                 terminal=row['Terminal'],
        #                 transactiontype=transaction_instance,
        #                 id_status=payment_instance,
        #                 divergencias=divergencias,
        #                 valor_liquido_venda=row['ValorLiquidoVenda'] if not pd.isna(row['ValorLiquidoVenda']) else None,
        #                 observacao=observacao,
        #                 motivo_ajuste=motivo_ajuste,
        #                 conta_adquirente=False if pd.isna(row['ContaAdquirente']) or row['ContaAdquirente'] == '' else True,
        #                 taxa_antecipacao=row['TaxaAntecipacao'] if not pd.isna(row['TaxaAntecipacao']) else None,
        #                 taxa_antecipacao_mensal=row['TaxaAntecipacaoMensal'] if not pd.isna(row['TaxaAntecipacaoMensal']) else None,
        #                 valor_taxa_antecipacao=row['ValorTaxaAntecipacao'] if not pd.isna(row['ValorTaxaAntecipacao']) else None,
        #                 valor_taxa=row['ValorTaxa'] if not pd.isna(row['ValorTaxa']) else None,
        #                 modality=modality_instance,
        #                 tem_conciliacao_bancaria=True if row['TemConciliacaoBancaria'] == 'Sim' else False,
        #                 cartao=row['Cartao']
        #             )
                    
        #             pagamento.save()
                    
        #         except Exception as e:
        #             print(f"Erro ao salvar o pagamento no índice {index}, ID {row['Id']} {row['DataPagamento']} {row['DataPrevistaPagamento']} {row['DataVenda']}: {str(e)}")
        #             # Imprime todas as variáveis e seus valores que estão sendo salvos
        #             print("Valores de pagamento que causaram o erro:")
        #             print(vars(pagamento))
                    
        #             # Parar o loop após o primeiro erro
        #             # break            
        #             continue
        #     self.stdout.write(self.style.SUCCESS("Dados coletados e armazenados com sucesso!"))
        # else:
        #     self.stdout.write(self.style.ERROR(f"Erro na requisição: {response.status_code}"))
