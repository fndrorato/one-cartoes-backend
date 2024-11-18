from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Received
from .serializers import ReceivedSerializer
from django.shortcuts import get_object_or_404

class ReceivedListView(APIView):
    # Exigir que o usuário esteja autenticado
    permission_classes = [IsAuthenticated]    
    
    def get(self, request, *args, **kwargs):
        # Parâmetros obrigatórios
        client_id = request.query_params.get('client_id')
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')

        # Verificar se todos os parâmetros estão presentes
        if not all([client_id, date_start, date_end]):
            return Response({"error": "Parâmetros 'cliente', 'data inicio' e 'data final' são obrigatórios."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filtro dos dados pelo client_id e datas
            received_records = Received.objects.filter(
                client_id=client_id,
                data_pagamento__range=[date_start, date_end]
            )[:10] 
            

            
            
            print(received_records.count())
            
            # received_data_list = [
            #     {
            #         'id': record.id,
            #         'id_pagamento': record.id_pagamento,
            #         'refo_id': record.refo_id,
            #         'estabelecimento': record.estabelecimento,
            #         'data_pagamento': record.data_pagamento,
            #         'data_prevista_pagamento': record.data_prevista_pagamento,
            #         'data_venda': record.data_venda,
            #         'autorizacao': record.autorizacao,
            #         'nsu': record.nsu,
            #         'id_transacao': record.id_transacao,
            #         'parcela': record.parcela,
            #         'total_parcelas': record.total_parcelas,
            #         'resumo_venda': record.resumo_venda,
            #         'valor_bruto': record.valor_bruto,
            #         'taxa': record.taxa,
            #         'outras_despesas': record.outras_despesas,
            #         'valor_liquido': record.valor_liquido,
            #         'idt_antecipacao': record.idt_antecipacao,
            #         'agencia': record.agencia,
            #         'conta': record.conta,
            #         'nome_loja': record.nome_loja,
            #         'terminal': record.terminal,
            #         'divergencias': record.divergencias,
            #         'valor_liquido_venda': record.valor_liquido_venda,
            #         'observacao': record.observacao,
            #         'motivo_ajuste': record.motivo_ajuste,
            #         'conta_adquirente': record.conta_adquirente,
            #         'taxa_antecipacao': record.taxa_antecipacao,
            #         'taxa_antecipacao_mensal': record.taxa_antecipacao_mensal,
            #         'valor_taxa_antecipacao': record.valor_taxa_antecipacao,
            #         'valor_taxa': record.valor_taxa,
            #         'tem_conciliacao_bancaria': record.tem_conciliacao_bancaria,
            #         'cartao': record.cartao,
            #         'client': record.client.id if record.client else None,
            #         'id_adquirente': record.adquirente.id if record.adquirente else None,
            #         'nome_adquirente': record.adquirente.name if record.adquirente else None,
            #         'id_produto': record.product.id if record.product else None,
            #         'nome_produto': record.product.name if record.product else None,
            #         'banco': record.banco,
            #         'id_tipo_transacao': record.transactiontype.id if record.transactiontype else None,
            #         'nome_tipo_transacao': record.transactiontype.name if record.transactiontype else None,
            #         # 'id_status_pagamento': record.paymentstatus.id if record.paymentstatus else None,
            #         # 'descricao_status_pagamento': record.paymentstatus.description if record.paymentstatus else None,
            #         'id_modalidade': record.modality.id if record.modality else None,
            #         'nome_modalidade': record.modality.name if record.modality else None
            #     }
            #     for record in received_records
            # ]


            # Serialização e retorno dos dados
            serializer = ReceivedSerializer(received_records, many=True)
            # return Response(received_data_list, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
