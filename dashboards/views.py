import os
import openpyxl
import uuid
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, OuterRef, Subquery, FloatField
from django.http import HttpResponse
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from payments.models import Received, Modality, ServicosPagos
from clients.models import Clients
from datetime import datetime
from .serializers import ModalityResultSerializer, SharedLinkSerializer
from .models import SharedLink

class SharedLinkCreateView(generics.CreateAPIView):
    queryset = SharedLink.objects.all()
    serializer_class = SharedLinkSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Gera um código único para o code_url
        unique_code = str(uuid.uuid4())  # Gera um UUID como código único
        serializer.save(created_by=self.request.user, code_url=unique_code)

    def create(self, request, *args, **kwargs):
        # Chama o método de criação padrão
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Retorna a resposta com o code_url
        return Response({'code_url': serializer.instance.code_url}, status=status.HTTP_201_CREATED)

class ReceivedDataView(APIView):
    
    # Exigir que o usuário esteja autenticado
    permission_classes = [IsAuthenticated]     

    # Helper para formatar o valor bruto
    def format_mil(self, value):
        return f"{value / 1000:,.2f} Mil".replace(",", "X").replace(".", ",").replace("X", ".")

    # Método para criar informações agregadas
    def create_info_numbers(self, query, tipo):
        valor_bruto_sum = query['valor_bruto_sum'] or 0
        valor_taxa_sum = query['valor_taxa_sum'] or 0
        value = float(valor_taxa_sum / valor_bruto_sum) * 100 if valor_bruto_sum > 0 else 0
        value = f"{value:.2f}%"  # Formata o valor como percentual

        # Dicionário de títulos e cores
        vetor = {
            'false': {
                'venda': "Venda Sem Antecipação",
                'despesa': "Despesa Sem Antecipação",
                'taxa': "Taxa Sem Antecipação",
                'color': "#7a4019"
            },
            'true': {
                'venda': "Venda Com Antecipação",
                'despesa': "Despesa Com Antecipação",
                'taxa': "Taxa Com Antecipação",
                'color': "#54B435"
            },   
            'total':{
                'venda': "Venda Total",
                'despesa': "Despesa Total",
                'taxa': "Taxa Total",
                'color': "#3871cb"                
            }
        }
        
        # Dicionário com as informações de retorno
        info_numbers = {
            "venda": {},
            "despesa": {},
            "taxa": {},
        }        

        # Preenche info_numbers com as informações formatadas
        info_numbers["venda"] = {
            "title": vetor[tipo]['venda'],
            "icon": "credit_card",
            "growth": 33,
            "value": self.format_mil(valor_bruto_sum),
            "color": vetor[tipo]['color']
        }
        
        info_numbers["despesa"] = {
            "title": vetor[tipo]['despesa'],
            "icon": "credit_card",
            "growth": 33,
            "value": self.format_mil(valor_taxa_sum),
            "color": vetor[tipo]['color']
        }
        
        info_numbers["taxa"] = {
            "title": vetor[tipo]['taxa'],
            "icon": "credit_card",
            "growth": 33,
            "value": value,
            "color": vetor[tipo]['color']
        }

        return info_numbers["venda"], info_numbers["despesa"], info_numbers["taxa"]
    
    def get_modality_numbers(self, client_id, date_start, date_end):
        # Filtra os registros de acordo com client_id e intervalo de data
        queryset = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).values('modality').annotate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )

        # Monta o resultado calculando a porcentagem e obtendo nome e ID da modality
        result = []
        for entry in queryset:
            modality_id = entry['modality']
            modality = get_object_or_404(Modality, id=modality_id)
            valor_bruto_sum = entry['valor_bruto_sum']
            valor_taxa_sum = entry['valor_taxa_sum'] or 0  # Caso `valor_taxa` seja `None`

            # Calcula a porcentagem (valor_taxa_sum / valor_bruto_sum) se valor_bruto_sum > 0
            value = valor_taxa_sum / valor_bruto_sum if valor_bruto_sum > 0 else 0
            value = float(value * 100) # convertendo para porcentagem
            
            if value > 0:
                result.append({
                    "id": modality.id,
                    "title": modality.name,  # Assumindo que o campo nome da modalidade é `name`
                    "value": value
                })
                
        # Serializa o resultado e retorna a resposta JSON
        modality_data = ModalityResultSerializer(result, many=True)  
        
        return modality_data      
    
    def get_info_numbers(self, queryset, client_id, date_start, date_end):
        # Info Numbers
        info_numbers = {
            "semAntecipacaoVenda":{},
            "semAntecipacaoDespesa":{},
            "semAntecipacaoTaxa":{},
            "antecipacaoVenda":{},
            "antecipacaoDespesa":{},
            "antecipacaoTaxa":{},
            "vendaTotal":{},
            "despesaTotal":{},
            "taxaTotal":{}
        }
        # Agregação para quando idt_antecipacao é False
        antecipacao_false = queryset.filter(
            idt_antecipacao=False,
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)            
        ).aggregate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )
        
        info_numbers["semAntecipacaoVenda"], info_numbers["semAntecipacaoDespesa"], info_numbers["semAntecipacaoTaxa"] = self.create_info_numbers(antecipacao_false, "false")

        # Agregação para quando idt_antecipacao é True
        antecipacao_true = queryset.filter(
            idt_antecipacao=True,
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).aggregate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )
        info_numbers["antecipacaoVenda"], info_numbers["antecipacaoDespesa"], info_numbers["antecipacaoTaxa"] = self.create_info_numbers(antecipacao_true, "true")
        
        # Soma total sem filtro
        total_received = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).aggregate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )
        
        info_numbers["vendaTotal"], info_numbers["despesaTotal"], info_numbers["taxaTotal"] = self.create_info_numbers(total_received, "total")
        
        return info_numbers
                
    def get_tipo_cartoes(self, client_id, date_start, date_end):
        # Query que agrupa os dados por `type_card` e produto
        queryset = (
            Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=(date_start, date_end)
            ).values(
                'product__type_card__name',  # Nome do tipo de cartão
                'product__name'              # Nome do produto
            )
            .annotate(
                venda_bruta=Sum('valor_bruto'),  # Soma do valor bruto
                valor_taxa=Sum('valor_taxa')     # Soma do valor taxa
            )
            .order_by('product__type_card__name')  # Ordena por tipo do cartão
        )       
        
        # Estrutura para o JSON de resposta
        tipo_cartoes = {}

        for entry in queryset:
            type_card_name = entry['product__type_card__name']
            product_name = entry['product__name']
            venda_bruta = entry['venda_bruta'] or 0
            valor_taxa = entry['valor_taxa'] or 0
            # Calcula a taxa percentual
            taxa_porcentagem = (valor_taxa / venda_bruta * 100) if venda_bruta else 0

            # Constrói cada entrada para o tipo de cartão
            product_data = {
                "name": product_name,
                "Venda Bruta": venda_bruta,
                "Taxa R$": valor_taxa,
                "Taxa%": round(taxa_porcentagem, 2)
            }

            # Adiciona os produtos agrupados por `type_card.name`
            if type_card_name not in tipo_cartoes:
                tipo_cartoes[type_card_name] = []
            tipo_cartoes[type_card_name].append(product_data)

        # Formata o JSON final
        tipo_cartoes_data = [
            {type_card_name: products} for type_card_name, products in tipo_cartoes.items()
        ]

        # Ajusta a estrutura final para retornar apenas um dicionário
        tipo_cartoes_final = [tipo_cartoes]  # Coloca em uma lista como requerido
 
        return tipo_cartoes_final        
    
    def get_adquirente(self, client_id, date_start, date_end):
        # Query que agrupa os dados por `acquirer`
        acquirer_queryset = (
            Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=(date_start, date_end)
            ).values(
                'adquirente__name'  # Nome do adquirente
            )
            .annotate(
                venda_bruta=Sum('valor_bruto'),  # Soma do valor bruto
                soma_valor_taxa=Sum('valor_taxa'),  # Soma do valor taxa
                taxa_percentual=(Sum('valor_taxa') / Sum('valor_bruto') * 100)  # Taxa percentual
            )
            .order_by('adquirente__name')  # Ordena por nome do adquirente
        )

        # Estrutura para o JSON de resposta
        adquirente_data = []

        for entry in acquirer_queryset:
            name = entry['adquirente__name']
            venda_bruta = entry['venda_bruta'] or 0
            soma_valor_taxa = entry['soma_valor_taxa'] or 0
            taxa_percentual = round(entry['taxa_percentual'], 2) if venda_bruta else 0

            # Cria a entrada para o adquirente
            acquirer_info = {
                "name": name,
                "Venda Bruta": venda_bruta,
                "Soma_de_Valor_Taxa": soma_valor_taxa,
                "Taxa%": taxa_percentual
            }
            adquirente_data.append(acquirer_info)

        return adquirente_data
                    
    def get_servicos_adicionais_pagos(self, client_id, date_start, date_end):
        # Query que agrupa os dados por `observacao`, somando `valor_liquido` onde for menor que 0
        observation_queryset = (
            Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=(date_start, date_end),
                valor_liquido__lt=0  # Filtra para incluir apenas valores líquidos menores que 0
            )
            .annotate(
                servicos_pagos_name=Subquery(
                    ServicosPagos.objects.filter(observacao=OuterRef('observacao')).values('name')[:1]
                )
            )
            .values('servicos_pagos_name')  # Agrupa pelo nome de ServicosPagos
            .annotate(
                total_liquido=Sum('valor_liquido')  # Soma dos valores líquidos
            )
            .order_by('-total_liquido')  # Ordena do maior para o menor
        )

        # Cálculo do valor total
        total_valor_liquido = observation_queryset.aggregate(total=Sum('total_liquido'))['total'] or 0

        # Estrutura para o JSON de resposta
        servicos_adicionais_pagos = [
            {
                "name": "Total",
                "Valor": round(total_valor_liquido * -1, 2)  # Total dos valores líquidos
            }
        ]

        # Adiciona cada entrada para observação ao JSON
        for entry in observation_queryset:
            observacao = entry['servicos_pagos_name'] or "Sem Observação"  # Use "Sem Observação" se for None
            valor_liquido = round(entry['total_liquido'] * -1, 2)  # Arredonda o valor líquido

            # Adiciona a observação ao JSON
            servicos_adicionais_pagos.append({
                "name": observacao,
                "Valor": valor_liquido
            })            

        servicos_adicionais_pagos = sorted(servicos_adicionais_pagos, key=lambda x: x['Valor'], reverse=True)
        
        return servicos_adicionais_pagos
                
    
    def get(self, request):
        client_id = request.query_params.get('client_id')
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')

        # Verifica se todos os parâmetros obrigatórios foram fornecidos
        if not (client_id and date_start and date_end):
            return Response({"error": "Parâmetros insuficientes."}, status=status.HTTP_400_BAD_REQUEST)

        # Converte strings de data para objetos datetime
        try:
            date_start = datetime.strptime(date_start, "%Y-%m-%d").date()
            date_end = datetime.strptime(date_end, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filtra os registros de acordo com client_id e intervalo de data
        queryset = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).values('modality').annotate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )

        # # Serializa o resultado e retorna a resposta JSON
        modality_data = self.get_modality_numbers(client_id, date_start, date_end)
        info_numbers = self.get_info_numbers(queryset, client_id, date_start, date_end)
        tipo_cartoes_final = self.get_tipo_cartoes(client_id, date_start, date_end)
        adquirente_data = self.get_adquirente(client_id, date_start, date_end)
        servicos_adicionais_pagos = self.get_servicos_adicionais_pagos(client_id, date_start, date_end)
        
        # Primeiro, calcula o valor bruto total para o client_id e no intervalo de datas
        total_venda_bruta = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).aggregate(total=Sum('valor_bruto'))['total'] or 0

        # Em seguida, calcula a venda bruta por tipo de cartão
        venda_por_tipo_cartao_queryset = (
            Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=(date_start, date_end),
                product__type_card__id__isnull=False  # Filtra para garantir que o ID do tipo de cartão não seja nulo
            )
            .values('product__type_card__id', 'product__type_card__name')  # Agrupa pelo ID e título do type_card
            .annotate(
                venda_bruta=Sum('valor_bruto')  # Soma das vendas brutas
            )
        )

        # Constrói a lista de resultados para vendaPorTipoCartao
        venda_por_tipo_cartao = []
        for entry in venda_por_tipo_cartao_queryset:
            tipo_cartao_id = entry['product__type_card__id']
            tipo_cartao_title = entry['product__type_card__name']
            venda_bruta = entry['venda_bruta']

            # Calcula a porcentagem em relação à venda bruta total
            if total_venda_bruta > 0:
                porcentagem = (venda_bruta / total_venda_bruta) * 100
            else:
                porcentagem = 0  # Se não houver vendas, a porcentagem é 0

            # Adiciona o dicionário ao resultado, formatando o valor para 2 casas decimais
            venda_por_tipo_cartao.append({
                "id": tipo_cartao_id,
                "title": tipo_cartao_title,
                "value": round(porcentagem, 2) 
            })       

        analytics_data = {
            "TaxaEfetiva": modality_data.data,
            "infoNumbers": info_numbers,
            "tipoCartoes": tipo_cartoes_final,
            "adquirente": adquirente_data,
            "servicosAdicionaisPagos": servicos_adicionais_pagos,
            "vendaPorTipoCartao": venda_por_tipo_cartao
        }        
        
        return Response(analytics_data, status=status.HTTP_200_OK)

# class SharedLinkDashboardView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         # Resposta genérica
#         data = {
#             "message": "Esta é uma resposta genérica para a requisição GET."
#         }
#         return Response(data, status=status.HTTP_200_OK)

class SharedLinkDashboardView(APIView): 
    permission_classes = [AllowAny]
         
    def get(self, request):
        # Obter parâmetros da URL
        code = request.query_params.get('code')
        # Validar parâmetros obrigatórios
        if not code:
            return Response({"error": "Código não encontrado."},
                            status=status.HTTP_400_BAD_REQUEST)        
        
        shared = get_object_or_404(SharedLink, code_url=code)
        client_id = shared.client.pk
        fantasy_name = shared.client.fantasy_name
        info_adicional = shared.info
        date_start = shared.date_start
        date_end = shared.date_end
        # Formatar as datas no padrão desejado
        date_start_formatted = date_start.strftime("%d/%m/%Y")
        date_end_formatted = date_end.strftime("%d/%m/%Y")

        # Criar o texto com a quebra de linha
        periodo_apuracao = f"{date_start_formatted} - {date_end_formatted}"
        
        # Filtra os registros de acordo com client_id e intervalo de data
        queryset = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).values('modality').annotate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )          
        
        # Obtenha o cliente pelo client_id e retorne o fantasy_name
        client = get_object_or_404(Clients, id=client_id)
        fantasy_name = client.fantasy_name        
        
        # Serializa o resultado e retorna a resposta JSON
        received_data_view = ReceivedDataView()
        modality_data = received_data_view.get_modality_numbers(client_id, date_start, date_end)
        info_numbers = received_data_view.get_info_numbers(queryset, client_id, date_start, date_end)
        tipo_cartoes_final = received_data_view.get_tipo_cartoes(client_id, date_start, date_end)
        adquirente_data = received_data_view.get_adquirente(client_id, date_start, date_end)
        servicos_adicionais_pagos = received_data_view.get_servicos_adicionais_pagos(client_id, date_start, date_end)          
        
        # Primeiro, calcula o valor bruto total para o client_id e no intervalo de datas
        total_venda_bruta = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).aggregate(total=Sum('valor_bruto'))['total'] or 0

        # Em seguida, calcula a venda bruta por tipo de cartão
        venda_por_tipo_cartao_queryset = (
            Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=(date_start, date_end),
                product__type_card__id__isnull=False  # Filtra para garantir que o ID do tipo de cartão não seja nulo
            )
            .values('product__type_card__id', 'product__type_card__name')  # Agrupa pelo ID e título do type_card
            .annotate(
                venda_bruta=Sum('valor_bruto')  # Soma das vendas brutas
            )
        )

        # Constrói a lista de resultados para vendaPorTipoCartao
        venda_por_tipo_cartao = []
        for entry in venda_por_tipo_cartao_queryset:
            tipo_cartao_id = entry['product__type_card__id']
            tipo_cartao_title = entry['product__type_card__name']
            venda_bruta = entry['venda_bruta']

            # Calcula a porcentagem em relação à venda bruta total
            if total_venda_bruta > 0:
                porcentagem = (venda_bruta / total_venda_bruta) * 100
            else:
                porcentagem = 0  # Se não houver vendas, a porcentagem é 0

            # Adiciona o dicionário ao resultado, formatando o valor para 2 casas decimais
            venda_por_tipo_cartao.append({
                "id": tipo_cartao_id,
                "title": tipo_cartao_title,
                "value": round(porcentagem, 2) 
            })       

        analytics_data = {
            "NomeFantasia": fantasy_name,
            "InfoAdicional": info_adicional,
            "Periodo": periodo_apuracao,
            "TaxaEfetiva": modality_data.data,
            "infoNumbers": info_numbers,
            "tipoCartoes": tipo_cartoes_final,
            "adquirente": adquirente_data,
            "servicosAdicionaisPagos": servicos_adicionais_pagos,
            "vendaPorTipoCartao": venda_por_tipo_cartao
        }        
        
        return Response(analytics_data, status=status.HTTP_200_OK)        


class ExportDashboardView(APIView):
    # Exigir que o usuário esteja autenticado
    permission_classes = [IsAuthenticated]         
    
    def get(self, request):
        # Obter parâmetros da URL
        client_id = request.query_params.get('client_id')
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        
        # Validar parâmetros obrigatórios
        if not client_id or not date_start or not date_end:
            return Response({"error": "Parâmetros 'client_id', 'date_start' e 'date_end' são obrigatórios."},
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Converte strings de data para objetos datetime
        try:
            date_start = datetime.strptime(date_start, "%Y-%m-%d").date()
            date_end = datetime.strptime(date_end, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filtra os registros de acordo com client_id e intervalo de data
        queryset = Received.objects.filter(
            client_id=client_id,
            data_pagamento__range=(date_start, date_end)
        ).values('modality').annotate(
            valor_bruto_sum=Sum('valor_bruto'),
            valor_taxa_sum=Sum('valor_taxa')
        )          
        
        # Obtenha o cliente pelo client_id e retorne o fantasy_name
        client = get_object_or_404(Clients, id=client_id)
        fantasy_name = client.fantasy_name        
        
        # Serializa o resultado e retorna a resposta JSON
        received_data_view = ReceivedDataView()
        # modality_data = received_data_view.get_modality_numbers(client_id, date_start, date_end)
        # info_numbers = received_data_view.get_info_numbers(queryset, client_id, date_start, date_end)
        # tipo_cartoes_final = received_data_view.get_tipo_cartoes(client_id, date_start, date_end)
        # adquirente_data = received_data_view.get_adquirente(client_id, date_start, date_end)
        # servicos_adicionais_pagos = received_data_view.get_servicos_adicionais_pagos(client_id, date_start, date_end)          

        # Caminho para o modelo do Excel em dashboards/excel_model/
        model_path = os.path.join(settings.BASE_DIR, 'dashboards', 'excel_model', 'dashboard_model.xlsx')
        
        # Carregar o modelo do Excel
        # workbook = load_workbook(model_path)
        workbook = openpyxl.load_workbook(model_path, read_only=False)

        sheet = workbook['Info']  # Use o nome exato da aba
        
        # # Colocando os dados básicos
        formatted_text = f'Período de Apuração {date_start.strftime("%d/%m/%Y")} - {date_end.strftime("%d/%m/%Y")}'
        sheet['B1'] = f'{fantasy_name}'
        sheet['B2'] = f'{formatted_text}'
        
        # Caminho para salvar o arquivo atualizado na pasta `media`
        # output_filename = f"dashboard_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        # output_path = os.path.join(settings.MEDIA_ROOT, 'exported_dashboards', output_filename)

        # Criar a pasta se não existir
        # os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salvar o workbook atualizado
        # workbook.save(output_path)
        workbook.save(model_path)
        
        return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Retornar o arquivo atualizado para download
        # with open(output_path, 'rb') as file:
        #     response = HttpResponse(
        #         file.read(),
        #         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        #     )
        #     response['Content-Disposition'] = f'attachment; filename={output_filename}'
        #     return response



def dashboard_view(request):
    analytics_data = {
        "TaxaEfetiva":[
            {
                "id": 1,
                "title": "Benefício",
                "value": 6.13 
            },
            {
                "id": 2,
                "title": "Crédito a Vista",
                "value": 2.55 
            },
            {
                "id": 3,
                "title": "Débito",
                "value": 1.32 
            },
            {
                "id": 4,
                "title": "Pix",
                "value": 0.48 
            },                                 
        ],
        "infoNumbers": {
            "semAntecipacaoVenda": {
                "title": "Venda Sem Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "1.580.70 Mil",
                "color": "#7a4019",
            },
            "semAntecipacaoDespesa": {
                "title": "Despesa Sem Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "39.77 Mil",
                "color": "#7a4019",
            },
            "semAntecipacaoTaxa": {
                "title": "Taxa Sem Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "2,52%",
                "color": "#7a4019",
            },
            "antecipacaoVenda": {
                "title": "Venda Com Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "255.31 Mil",
                "color": "#54B435",
            },
            "antecipacaoDespesa": {
                "title": "Despesa Com Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "15.35 Mil",
                "color": "#54B435",
            },
            "antecipacaoTaxa": {
                "title": "Taxa com Antecipação",
                "icon": "credit_card",
                "growth": 33,
                "value": "6,00%",
                "color": "#54B435",
            },   
            "vendaTotal": {
                "title": "Venda Total",
                "icon": "credit_card",
                "growth": 33,
                "value": "1.836.01 Mil",
                "color": "#3871cb",
            },
            "despesaTotal": {
                "title": "Despesa Total",
                "icon": "credit_card",
                "growth": 33,
                "value": "55.09 Mil",
                "color": "#3871cb",
            },
            "taxaTotal": {
                "title": "Taxa Total Cartão",
                "icon": "credit_card",
                "growth": 33,
                "value": "3,00%",
                "color": "#3871cb",
            }
        },
        "tipoCartoes":[
            {
                "Credito": [
                    {
                        "name": "VISA CREDITO A VISTA",
                        "Venda Bruta": 177865.31,
                        "Taxa R$": 4400.62,
                        "Taxa%": 2.47
                    },
                    {
                        "name": "MASTER CREDITO",
                        "Venda Bruta": 306684.54,
                        "Taxa R$": 7293.37,
                        "Taxa%": 2.38
                    },
                    {
                        "name": "PRÉ-PAGO ELO CRÉDITO",
                        "Venda Bruta": 8936.62,
                        "Taxa R$": 304.21,
                        "Taxa%": 3.40
                    },
                    {
                        "name": "PRÉ-PAGO VISA CREDITO",
                        "Venda Bruta": 7641.05,
                        "Taxa R$": 147.71,
                        "Taxa%": 1.93
                    },
                    {
                        "name": "ELO CREDITO",
                        "Venda Bruta": 45188.95,
                        "Taxa R$": 1625.29,
                        "Taxa%": 3.60
                    },
                    {
                        "name": "PRÉ-PAGO MASTER CRÉDITO",
                        "Venda Bruta": 2143.96,
                        "Taxa R$": 74.95,
                        "Taxa%": 3.50
                    },
                    {
                        "name": "TRICARD CRÉDITO À VISTA",
                        "Venda Bruta": 16081.45,
                        "Taxa R$": 514.58,
                        "Taxa%": 3.20
                    },
                    {
                        "name": "AMEX CREDITO A VISTA",
                        "Venda Bruta": 2111.17,
                        "Taxa R$": 72.14,
                        "Taxa%": 3.42
                    },
                    {
                        "name": "HIPERCARD CREDITO A VISTA",
                        "Venda Bruta": 156.60,
                        "Taxa R$": 8.39,
                        "Taxa%": 5.36
                    }
                ],
                "Debito": [
                    {
                        "name": "MAESTRO",
                        "Venda Bruta": 282050.31,
                        "Taxa R$": 2820.43,
                        "Taxa%": 1.00
                    },
                    {
                        "name": "PRÉ-PAGO VISA DÉBITO",
                        "Venda Bruta": 37503.72,
                        "Taxa R$": 457.79,
                        "Taxa%": 1.22
                    },
                    {
                        "name": "VISA ELECTRON DEBITO A VISTA",
                        "Venda Bruta": 277700.84,
                        "Taxa R$": 3230.42,
                        "Taxa%": 1.16
                    },
                    {
                        "name": "ELO DEBITO A VISTA",
                        "Venda Bruta": 151115.83,
                        "Taxa R$": 3107.61,
                        "Taxa%": 2.06
                    },
                    {
                        "name": "PRÉ-PAGO MASTER DÉBITO",
                        "Venda Bruta": 22834.11,
                        "Taxa R$": 552.53,
                        "Taxa%": 2.42
                    },
                    {
                        "name": "PRÉ-PAGO ELO DÉBITO",
                        "Venda Bruta": 224.91,
                        "Taxa R$": 5.62,
                        "Taxa%": 2.50
                    },
                    {
                        "name": "PIX",
                        "Venda Bruta": 35.60,
                        "Taxa R$": 0.17,
                        "Taxa%": 0.48
                    }
                ],
                "Voucher": [
                    {
                        "name": "VALECARD VOUCHER",
                        "Venda Bruta": 13688.32,
                        "Taxa R$": 889.79,
                        "Taxa%": 6.50
                    },                    
                    {
                        "name": "ALELO ALIMENTAÇÃO",
                        "Venda Bruta": 128732.07,
                        "Taxa R$": 8367.75,
                        "Taxa%": 6.50
                    },
                    {
                        "name": "ALELO REFEIÇÃO",
                        "Venda Bruta": 22144.82,
                        "Taxa R$": 1439.39,
                        "Taxa%": 6.50
                    },
                    {
                        "name": "SODEXO PREMIUM PASS",
                        "Venda Bruta": 547.87,
                        "Taxa R$": 32.88,
                        "Taxa%": 6.00
                    },
                    {
                        "name": "SODEXO REFEICAO",
                        "Venda Bruta": 2814.57,
                        "Taxa R$": 168.88,
                        "Taxa%": 6.00
                    },
                    {
                        "name": "SODEXO ALIMENTACAO",
                        "Venda Bruta": 251947.62,
                        "Taxa R$": 15117.24,
                        "Taxa%": 6.00
                    },
                    {
                        "name": "ALELO MULTIBENEFÍCIOS",
                        "Venda Bruta": 957.47,
                        "Taxa R$": 62.24,
                        "Taxa%": 6.50
                    },
                    {
                        "name": "TICKET ALIMENTACAO",
                        "Venda Bruta": 37257.34,
                        "Taxa R$": 1956.08,
                        "Taxa%": 5.25
                    },
                    {
                        "name": "TICKET REFEICAO",
                        "Venda Bruta": 3112.40,
                        "Taxa R$": 196.09,
                        "Taxa%": 6.30
                    },
                    {
                        "name": "VR ALIMENTACAO",
                        "Venda Bruta": 32413.00,
                        "Taxa R$": 2042.06,
                        "Taxa%": 6.30
                    },
                    {
                        "name": "VR REFEICAO",
                        "Venda Bruta": 1812.07,
                        "Taxa R$": 114.16,
                        "Taxa%": 6.30
                    },
                    {
                        "name": "TICKET FLEX",
                        "Venda Bruta": 1259.37,
                        "Taxa R$": 66.12,
                        "Taxa%": 5.25
                    },
                    {
                        "name": "VALESHOP DÉBITO",
                        "Venda Bruta": 10.38,
                        "Taxa R$": 0.62,
                        "Taxa%": 5.97
                    },
                    {
                        "name": "CABAL VOUCHER",
                        "Venda Bruta": 698.46,
                        "Taxa R$": 20.96,
                        "Taxa%": 3.00
                    }
                ]
            }
        ],
        "adquirente": [
            {
                "name": "Alelo",
                "Venda Bruta": 152172.32,
                "Soma_de_Valor_Taxa": "R$ 9.869,38",
                "Taxa%": 6.49
            },
            {
                "name": "Cabal",
                "Venda Bruta": 698.46,
                "Soma_de_Valor_Taxa": "R$ 20,96",
                "Taxa%": 3.00
            },
            {
                "name": "Cielo",
                "Venda Bruta": 309304.62,
                "Soma_de_Valor_Taxa": "R$ 11.449,97",
                "Taxa%": 3.70
            },
            {
                "name": "Getnet",
                "Venda Bruta": 1012888.90,
                "Soma_de_Valor_Taxa": "R$ 12.651,28",
                "Taxa%": 1.25
            },
            {
                "name": "Sodexo",
                "Venda Bruta": 255310.06,
                "Soma_de_Valor_Taxa": "R$ 15.319,00",
                "Taxa%": 6.00
            },
            {
                "name": "Ticket",
                "Venda Bruta": 41629.11,
                "Soma_de_Valor_Taxa": "R$ 2.218,29",
                "Taxa%": 5.33
            },
            {
                "name": "Tricard",
                "Venda Bruta": 16081.45,
                "Soma_de_Valor_Taxa": "R$ 514,58",
                "Taxa%": 3.20
            },
            {
                "name": "Valecard",
                "Venda Bruta": 13688.32,
                "Soma_de_Valor_Taxa": "R$ 889,79",
                "Taxa%": 6.50
            },
            {
                "name": "Valeshop",
                "Venda Bruta": 10.38,
                "Soma_de_Valor_Taxa": "R$ 0,62",
                "Taxa%": 5.97
            },
            {
                "name": "VR",
                "Venda Bruta": 34225.07,
                "Soma_de_Valor_Taxa": "R$ 2.156,22",
                "Taxa%": 6.30
            }
        ],
        "servicosAdicionaisPagos":[
            {
                "name": "Total",
                "Valor": 10328
            },
            {
                "name": "ANUIDADE (TICKET)",
                "Valor": 9364
            },
            {
                "name": "VALOR DA ANUIDADE (VR)",
                "Valor": 385
            },
            {
                "name": "(Em branco)",
                "Valor": 262
            },
            {
                "name": "HELP DESK (SODEXO)",
                "Valor": 180
            },                                                
            {
                "name": "TARIFA BANCÁRIA (TICKET & VR)",
                "Valor": 137
            }            
        ],
        "vendaPorTipoCartao":[
            {
                "id": 1,
                "title": "Débito",
                "value": 42.04 
            },
            {
                "id": 2,
                "title": "Crédito",
                "value": 30.87
            },
            {
                "id": 3,
                "title": "Voucher",
                "value": 27.09
            },                               
        ],        
    }
    
    return JsonResponse(analytics_data, safe=False)
