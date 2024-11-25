from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from decimal import Decimal
from .models import Received, ReceivedUpdateLog
from .serializers import ReceivedSerializer

def serialize_decimal(value):
    """Converte valores Decimal em float ou str para ser serializável em JSON."""
    return float(value) if isinstance(value, Decimal) else value

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
            ).select_related(
                'modality', 'product', 'adquirente', 'transactiontype', 'id_status'
            )[:10]
            
            if not received_records.exists():
                return Response({"detail": "Nenhum registro encontrado."}, status=status.HTTP_404_NOT_FOUND)            
            # Serialização e retorno dos dados
            serializer = ReceivedSerializer(received_records, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("error", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateReceivedView(APIView):
    """
    View para atualizar um registro do modelo Received e registrar as alterações.
    """
    
    # Exigir que o usuário esteja autenticado
    permission_classes = [IsAuthenticated]     

    def put(self, request, pk):
        
        try:
            # Busca a instância do modelo Received
            received_instance = Received.objects.get(pk=pk)
        except Received.DoesNotExist:
            return Response(
                {"error": "Registro não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Define os dados antes da atualização
        before_update = {
            "valor_bruto": serialize_decimal(received_instance.valor_bruto),
            "observacao": received_instance.observacao,
            "motivo_ajuste": received_instance.motivo_ajuste,
        }
        
        # Valida e atualiza os dados com o serializer
        serializer = ReceivedSerializer(
            received_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # Serializa os dados novos (após a atualização)
            after_update = {
                "valor_bruto": serialize_decimal(request.data.get("valor_bruto", received_instance.valor_bruto)),
                "observacao": request.data.get("observacao", received_instance.observacao),
                "motivo_ajuste": request.data.get("motivo_ajuste", received_instance.motivo_ajuste),
            }

            try:
                # Cria o log da atualização
                ReceivedUpdateLog.objects.create(
                    received=received_instance,
                    before_update=before_update,
                    after_update=after_update,
                    updated_by=request.user if request.user.is_authenticated else None,
                    updated_at=now(),
                )
            except Exception as e:
                # Captura e registra o erro
                print("Erro ao salvar log de atualização: %s", str(e))
            
            response_data = {
                "success": True,
                "message": "Pagamento atualizado com sucesso.",
                "status": status.HTTP_200_OK
            }       

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)