from django.db import models
from django.contrib.auth import get_user_model
import uuid
from clients.models import Clients
from django.utils import timezone

User = get_user_model()

class LogExport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_log_dashboard')
    client = models.JSONField(default=list, blank=True, null=True)
    log = models.TextField(null=True, blank=True)
    resultado = models.BooleanField(default=True)
    date_start = models.DateField()
    date_end = models.DateField()    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.client} - {'Sucesso' if self.resultado else 'Falha'}"
    
    def save_log(self, user, log, resultado, client, date_start, date_end):
        self.user = user
        self.log = log
        self.resultado = resultado
        self.client = client
        self.date_start = date_start
        self.date_end = date_end
        self.created_at = timezone.now()
        self.save()    


class SharedLink(models.Model):
    code_url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Gera um código único
    client = models.JSONField(default=list, blank=True, null=True)
    info = models.TextField(null=True, blank=True)
    date_start = models.DateField()
    date_end = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shared_links')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    info_action_01 = models.CharField(max_length=80, default='', null=True, blank=True)
    action_01 = models.CharField(max_length=80, default='', null=True, blank=True)
    info_action_02 = models.CharField(max_length=80, default='', null=True, blank=True)
    action_02 = models.CharField(max_length=80, default='', null=True, blank=True)
    info_action_03 = models.CharField(max_length=80, default='', null=True, blank=True)
    action_03 = models.CharField(max_length=80, default='', null=True, blank=True)
    info_action_04 = models.CharField(max_length=80, default='', null=True, blank=True)
    action_04 = models.CharField(max_length=80, default='', null=True, blank=True)
    download_url = models.CharField(max_length=255, null=True, blank=True, default='')

    def __str__(self):
        return str(self.code_url)
