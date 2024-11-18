from rest_framework import generics, permissions
from .models import Groups, Clients
from .serializers import GroupsSerializer, ClientSerializer
from rest_framework.permissions import IsAuthenticated

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer
    permission_classes = [IsAuthenticated]  # Garante que o usuário está autenticado

    def perform_create(self, serializer):       
        # O usuário autenticado será automaticamente atribuído ao `created_by`
        serializer.save(created_by=self.request.user)

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Groups.objects.all().order_by('name')
    serializer_class = GroupsSerializer
    permission_classes = [IsAuthenticated]  # Garante que o usuário está autenticado

    def get_queryset(self):        
        # O usuário só pode manipular os grupos que ele criou
        return Groups.objects.filter(created_by=self.request.user)
    
class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]  # Garante que o usuário está autenticado

    def perform_create(self, serializer):
        # Obtém o CNPJ do request e remove os caracteres não numéricos
        cnpj = self.request.data.get('cnpj', '')
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))  # Mantém apenas os números

        # Passa o CNPJ limpo para o serializer e salva o cliente
        serializer.save(cnpj=clean_cnpj, created_by=self.request.user)

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]  # Garante que o usuário está autenticado

    def get_queryset(self):
        return Clients.objects.filter(created_by=self.request.user)  # Filtra os clientes criados pelo usuário
