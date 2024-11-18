# users/models.py
import os
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.core.files.storage import default_storage
from django.db import models
from datetime import datetime
from PIL import Image
import random
import string
# from clients.models import Clients

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo email é obrigatório')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário precisa ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)  # Telefone
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_client_id = models.JSONField(default=list, blank=True, null=True)
    last_start_date = models.DateField(null=True, blank=True)
    last_end_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Novo campo de imagem
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)  
    raw_password = models.CharField(max_length=128, blank=True, null=True)  
    verify_number = models.IntegerField(default=0, null=True, blank=True)
    verify_number_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def generate_temporary_password(self, length=8):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))    
    
    def save(self, *args, **kwargs):
        # Verifica se há uma imagem sendo enviada
        if self.profile_image and not isinstance(self.profile_image, str):
            # Verifica se a nova imagem é diferente da imagem atual no banco de dados
            if self.pk is not None:  # Garante que o objeto já foi salvo e possui um ID
                current_instance = self.__class__.objects.get(pk=self.pk)  # Recupera a instância atual do banco de dados
                if current_instance.profile_image and current_instance.profile_image.name == self.profile_image.name:
                    return super().save(*args, **kwargs)  # Não faz nada se a imagem não mudou
          
            # Cria um novo nome de arquivo baseado na data e hora atual
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')  # Formato: anomesdiahoraminutomilisegundo
            extension = os.path.splitext(self.profile_image.name)[1]  # Obtém a extensão original da imagem
            new_filename = f'{timestamp}{extension}'

            # Define o novo nome para a imagem (sem alterar o diretório)
            self.profile_image.name = f'{new_filename}'

        # Primeiro, salva o objeto para garantir que ele tenha um ID
        super().save(*args, **kwargs)

        # Redimensiona a imagem após o salvamento
        if self.profile_image and default_storage.exists(self.profile_image.path):
            img = Image.open(self.profile_image.path)

            # Redimensiona a imagem se for maior que 128x128
            if img.height > 128 or img.width > 128:
                output_size = (128, 128)
                img.thumbnail(output_size)  # Redimensiona mantendo a proporção
                img.save(self.profile_image.path)  # Sobrescreve a imagem redimensionada    
