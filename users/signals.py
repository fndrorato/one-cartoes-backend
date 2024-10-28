# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings  # Importa as configurações
from .models import CustomUser

# @receiver(post_save, sender=CustomUser)
# def send_welcome_email(sender, instance, created, **kwargs):
#     if created:  # Apenas envia o e-mail quando um novo usuário é criado
#         subject = 'Bem-vindo ao nosso serviço!'
#         message = f'Seja bem-vindo, {instance.full_name}!\n\n' \
#                   f'Seu usuário: {instance.email}\n' \
#                   f'Sua senha provisória: 1234'  # Usar raw_password se você armazená-lo

#         try:
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
#             print('E-mail enviado com sucesso!')
#         except Exception as e:
#             print(f'Ocorreu um erro ao enviar o e-mail: {e}')
            
@receiver(post_save, sender=CustomUser)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Bem-vindo ao nosso serviço!'
        message = f'''
        Olá {instance.full_name},

        Bem-vindo ao nosso serviço! Seu usuário é {instance.email} e sua senha provisória é {instance.raw_password}

        Recomendamos que você altere sua senha após o primeiro acesso.

        Atenciosamente,
        Sua Equipe
        '''

        try:
            # Envia o e-mail
            sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
            if sent:  # Verifica se o e-mail foi enviado
                print(f"E-mail de boas-vindas enviado com sucesso para {instance.email}.")
            else:
                print(f"Falha ao enviar o e-mail de boas-vindas para {instance.email}.")
        except Exception as e:
            print(f"Ocorreu um erro ao enviar o e-mail: {e}")            
