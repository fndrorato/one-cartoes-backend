from django.db import models
from clients.models import Clients
from django.contrib.auth import get_user_model

User = get_user_model()

# Model de Adquirente
    
class Acquirer(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f"{self.name}"