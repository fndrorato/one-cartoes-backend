import secrets
import string
import random
import datetime
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings  # Importa as configurações
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)  # Campo personalizado para o nome do grupo
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name',  'password', 'raw_password', 'is_active', 'group', 'group_name', 'is_staff', 'profile_image', 'phone']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}  # Torna a senha opcional
        }

    def create(self, validated_data):
        group = validated_data.pop('group', None)  # Remove os grupos de validated_data
        password = validated_data.get('password', None)
        raw_password = ''
        
        if not password:
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))  # Senha de 10 caracteres
            raw_password = password
            
        # Remova a chave 'profile_image' do validated_data antes de passar para create_user
        profile_image = validated_data.pop('profile_image', None)
                
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            password=password
        )
        
        if group:
            user.group = group 
            
        # Agora atribua a imagem de perfil, se estiver presente
        if profile_image:
            user.profile_image = profile_image
            user.save()  # Salve novamente para persistir a imagem no banco de dados
        else:
            # Atribua os grupos ao usuário
            user.save()  
            
        self.send_welcome_email(user.full_name, user.email, raw_password)      
             
        return user
    
    def send_welcome_email(self, full_name, email, raw_password):
        subject = "One Conciliadora - Bem-vindo ao nosso serviço"
        message = f'''
        Olá {full_name},

        Bem-vindo ao nosso serviço! Seu usuário é {email} e sua senha provisória é: {raw_password}

        Recomendamos que você altere sua senha após o primeiro acesso.
        
        Acesse {settings.FRONTEND_URL}

        Atenciosamente,
        Sua Equipe
        '''        

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])    

    def update(self, instance, validated_data):
        group = validated_data.get('group', instance.group)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.full_name = validated_data.get('full_name', instance.full_name)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']
            
        # Atualize os grupos se fornecidos
        instance.group = group           

        instance.save()
        return instance
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']  # Inclui tanto o id quanto o name  

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise serializers.ValidationError('Credenciais inválidas.')

        else:
            raise serializers.ValidationError('Todos os campos são obrigatórios.')

        data['user'] = user
        return data        

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone', 'profile_image']
        
    def update(self, instance, validated_data):
        instance.phone = validated_data.get('phone', instance.phone)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        

        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']       

        instance.save()
        return instance      
    
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        """
        Verifica se a nova senha e a confirmação correspondem e se a senha atual está correta.
        """
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("A nova senha e a confirmação não coincidem.")
        
        user = self.context['request'].user  # Obter o usuário autenticado
        if not check_password(data['current_password'], user.password):
            raise serializers.ValidationError("A senha atual está incorreta.")
        
        return data    
    
class UserLastClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['last_client_id', 'last_start_date', 'last_end_date']  # Campos que podem ser atualizados      

    def validate(self, data):
        """
        Validações personalizadas para garantir que:
        - last_start_date não é vazio
        - last_end_date não é vazio
        - last_start_date é anterior ao last_end_date
        - last_end_date não é maior que a data de hoje
        """
        last_start_date = data.get('last_start_date')
        last_end_date = data.get('last_end_date')

        # Valida se as datas não estão vazias
        if not last_start_date:
            raise serializers.ValidationError("A data inicial não pode estar vazia.")
        if not last_end_date:
            raise serializers.ValidationError("A data final não pode estar vazia.")

        # Valida se start_date é menor que end_date
        if last_start_date and last_end_date and last_start_date > last_end_date:
            raise serializers.ValidationError("A data inicial deve ser menor que a data final.")

        # Valida se end_date não é maior que hoje
        if last_end_date and last_end_date > timezone.now().date():
            raise serializers.ValidationError("A data final não pode ser maior que a data de hoje.")

        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        # Verifica se o e-mail existe no banco de dados
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return email

    def create(self, validated_data):
        email = validated_data['email']
        user = CustomUser.objects.get(email=email)
        
        # Gera o código temporário
        verify_number = random.randint(100000, 999999)
        user.verify_number = verify_number
        user.verify_number_expiry = timezone.now() + datetime.timedelta(hours=24)
        user.save()

        # Envia o e-mail com o código
        subject = "Recuperação de senha"
        message = f'''
        Olá {user.full_name},

        Use este código para resetar a sua senha.
        
        Código: {user.verify_number}
        
        Acesse {settings.FRONTEND_URL}/reset-password

        Atenciosamente,
        Sua Equipe
        '''        

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])           
        
        return validated_data        
         