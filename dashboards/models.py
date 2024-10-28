from django.db import models
from django.contrib.auth import get_user_model
import uuid
from clients.models import Clients

User = get_user_model()

class SharedLink(models.Model):
    code_url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Gera um código único
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='shared_links')
    info = models.TextField()
    date_start = models.DateField()
    date_end = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shared_links')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.code_url)
