from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Groups(models.Model):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_groups')    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Clients(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.PROTECT)  # Chave estrangeira para o modelo Group
    cnpj = models.CharField(max_length=20)  # CNPJ com 14 caracteres
    name = models.CharField(max_length=255)  # Nome do cliente
    fantasy_name = models.CharField(max_length=255)  # Nome fantasia
    direction_street = models.CharField(max_length=255, null=True, blank=True)  # Rua
    direction_street_number = models.CharField(max_length=30, null=True, blank=True)  # Número
    direction_street_complement = models.CharField(max_length=50, blank=True, null=True)  # Complemento
    direction_zip_code = models.CharField(max_length=10)  # CEP
    direction_neighborhood = models.CharField(max_length=255, null=True, blank=True)  # Bairro
    direction_city = models.CharField(max_length=255)  # Cidade
    direction_state = models.CharField(max_length=2)  # Estado (sigla de 2 caracteres)
    email = models.EmailField(max_length=255)  # E-mail
    phone = models.CharField(max_length=15, blank=True)  # Telefone
    notes = models.TextField(blank=True)  # Notas adicionais
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_clients')    
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização

    def __str__(self):
        return self.name    
