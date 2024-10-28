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
            )

            # Serialização e retorno dos dados
            serializer = ReceivedSerializer(received_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
