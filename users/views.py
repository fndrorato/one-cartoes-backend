# views.py
import logging
import calendar
from rest_framework import status
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from jwt import decode as jwt_decode
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CustomUser
from clients.models import Clients
from .serializers import (
    CustomUserSerializer, GroupSerializer, 
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserLastClientUpdateSerializer,
    ForgotPasswordSerializer)

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Claims personalizados podem ser adicionados ao token, mas não necessário aqui
        return token

class CustomTokenView(TokenObtainPairView, TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer  # Serializer para POST (obter token)

    def post(self, request, *args, **kwargs):
        # Lógica do método POST (TokenObtainPairView)
        errors = []
        try:
            response = super().post(request, *args, **kwargs)
            user = self.get_user_data(request.data.get('email'))
            
            # Verifica se o caminho do profile_image existe
            if user.profile_image:
                profile_image_url = request.build_absolute_uri(user.profile_image.url)
            else:
                profile_image_url = None  # Ou um placeholder padrão
            
            if not user.last_start_date:
                user.last_start_date, user.last_end_date = self.get_last_data()
                user.save(update_fields=['last_start_date', 'last_end_date'])                

            clients = Clients.objects.all() 

            # Formatar a lista de clientes
            clients_data = sorted(
                [{'id': client.id, 'fantasy_name': client.fantasy_name} for client in clients],
                key=lambda x: x['fantasy_name']
            )

            if not user.last_client_id and clients_data:
                user.last_client_id = clients_data[0]['id']
                user.save(update_fields=['last_client_id'])  # Salva a mudança no banco de dados
            
            client_ids = user.last_client_id
            
            response_data = {
                'id': 11,
                'uid': user.id,
                'displayName': f'{user.full_name}',
                'photoURL': profile_image_url,
                'email': user.email,                
                'phone': user.phone,   
                'role': 'admin',  # Altere para o papel correto                
                'token': response.data['access'],
                'id_client_selected': client_ids,
                'start_date': user.last_start_date,
                'start_date': user.last_end_date,
                'clients': clients_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except InvalidToken:
            errors.append({
                'type': 'token',
                'message': 'Token inválido. Verifique suas credenciais.'
            })
            return Response({'errors': errors}, status=status.HTTP_401_UNAUTHORIZED)

        except AuthenticationFailed:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email:
                error_message =  'E-mail não encontrado.'
                errors.append({'type': 'email', 'message': 'E-mail não encontrado.'})
            if not password:
                error_message =  'Verifique a senha.'
                errors.append({'type': 'password', 'message': 'Verifique a senha.'})
            if email and password:
                error_message = 'Usuário ou senha incorretos'
                errors.append({'type': 'auth', 'message': 'Usuário ou senha incorretos.'})

            return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"Exceção capturada: {type(e).__name__}: {str(e)}")
            error_message = 'Usuário não encontrado.'
            errors.append({'type': 'email', 'message': 'Usuário não encontrado.'})
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        # Lógica do método GET (TokenRefreshView)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
        else:
            return Response({"error": "Token não fornecido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = self.get_user_id_from_token(access_token)
        except Exception as e:
            return Response({"error": f"Token inválido: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if user.profile_image:
            profile_image_url = request.build_absolute_uri(user.profile_image.url)
        else:
            profile_image_url = None  # Ou um placeholder padrão
            
        if not user.last_start_date:
            user.last_start_date, user.last_end_date = self.get_last_data()
            user.save(update_fields=['last_start_date', 'last_end_date'])                

        clients = Clients.objects.all() 

        # Formatar a lista de clientes
        clients_data = sorted(
            [{'id': client.id, 'fantasy_name': client.fantasy_name} for client in clients],
            key=lambda x: x['fantasy_name']
        )

        
        if not user.last_client_id and clients_data:
            user.last_client_id = clients_data[0]['id']
            user.save(update_fields=['last_client_id'])  # Salva a mudança no banco de dados
        
        client_ids = user.last_client_id
                                
        response_data = {
            'id': user.id,
            'uid': user.id,
            'displayName': f'{user.full_name}',
            'photoURL': profile_image_url,
            'email': user.email, 
            'phone': user.phone,                  
            'role': 'admin',  # Altere para o papel correto                
            'token': access_token, 
            'id_client_selected': client_ids,
            'start_date': user.last_start_date,
            'end_date': user.last_end_date,
            'clients': clients_data            
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    def get_user_data(self, email):
        User = get_user_model()
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_last_data(self):
        # Data atual
        today = datetime.today()

        # Mês e ano do mês passado
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1

        # Data inicial do mês passado
        first_day_last_month = datetime(year, last_month, 1)

        # Último dia do mês passado
        last_day_last_month = calendar.monthrange(year, last_month)[1]
        last_date_last_month = datetime(year, last_month, last_day_last_month)

        return first_day_last_month, last_date_last_month
    
    def get_user_id_from_token(self, token):
        try:
            decoded_data = jwt_decode(token, api_settings.SIGNING_KEY, algorithms=["HS256"])
            return decoded_data.get('user_id')
        except Exception as e:
            raise e

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser) 
    permission_classes = [IsAuthenticated]  # Exige autenticação para todas as operações
    
    def perform_create(self, serializer):
        user = serializer.save()
        logger.debug(f'Usuário criado: {user.email}, Imagem: {user.profile_image}')    

    def destroy(self, request, *args, **kwargs):
        user_to_delete = self.get_object()

        # Verifica se o usuário está tentando deletar a si mesmo
        if user_to_delete == request.user:
            return Response(
                {"message": "Você não pode deletar a si mesmo."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verifica se o usuário é um administrador
        if not request.user.is_staff:  # Supondo que 'is_staff' indica que o usuário é um administrador
            return Response(
                {"message": "Somente administradores podem deletar usuários."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Exclui a imagem de perfil se existir
        if user_to_delete.profile_image:
            default_storage.delete(user_to_delete.profile_image.path)

        # Deleta o usuário
        user_to_delete.delete()
        logger.debug(f'Usuário deletado: {user_to_delete.email}')
        return Response(status=status.HTTP_204_NO_CONTENT)        
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]  # Somente admins podem criar grupos    

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Retorna o usuário autenticado

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            print(f'Nome do arquivo: {profile_image.name}')
            print(f'Tamanho do arquivo: {profile_image.size}')
            print(f'Tipo do arquivo: {profile_image.content_type}')
                    
        serializer = UserUpdateSerializer(user, data=request.data)  # Atualização completa

        if serializer.is_valid():
            serializer.save()  # Salva as mudanças no banco de dados
            # Verifica se o usuário tem uma imagem de perfil atualizada
            if user.profile_image:
                profile_image_url = request.build_absolute_uri(user.profile_image.url)
            else:
                profile_image_url = None  # Ou um placeholder padrão

            # Modifica a resposta para incluir a URL completa da imagem
            response_data = serializer.data
            response_data['photoURL'] = profile_image_url  # URL completa da imagem de perfil

            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):   
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Atualiza a senha do usuário
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({"message": "Senha atualizada com sucesso."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserChangeClientUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Garante que o usuário esteja autenticado

    def put(self, request, *args, **kwargs):
        user = self.request.user  # O usuário autenticado vem do token JWT
        print(request.data)
        serializer = UserLastClientUpdateSerializer(user, data=request.data, partial=True)  # partial=True permite atualização parcial
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("ForgotPasswordView foi instanciada!")

    @csrf_exempt  # Ignora CSRF para esta view
    def post(self, request):
        logger.info(f"Headers: {dict(request.headers)}")  
        logger.info(f"Body: {request.body.decode('utf-8')}")
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Cria o código e envia o e-mail
            return Response({'message': 'Verification code sent to email'}, status=status.HTTP_200_OK)
        
        logger.warning("Serializer não foi válido!")
        logger.warning(f"Erros: {serializer.errors}")
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @csrf_exempt  # Ignora CSRF para esta view
    def post(self, request):
        verify_number = request.data.get('verify_number')
        new_password = request.data.get('new_password')
        
        try:
            User = get_user_model()
            user = User.objects.get(verify_number=verify_number)
            
            # Verifica se o código ainda é válido
            if timezone.now() > user.verify_number_expiry:
                return Response({'error': 'Código de verificação expirou'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Atualiza a senha do usuário
            user.set_password(new_password)
            user.verify_number = None
            user.verify_number_expiry = None
            user.save()
            
            return Response({'message': 'Senha alterada com sucesso'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)
        

@csrf_exempt  # Para facilitar testes, mas em produção é melhor usar proteção CSRF
def upload_profile_image(request):
    if request.method == 'POST':
        # Imprimir dados não-file
        print("Dados não-file:", request.POST)

        # Imprimir dados de arquivos
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            print(f'Nome do arquivo: {profile_image.name}')
            print(f'Tamanho do arquivo: {profile_image.size}')
            print(f'Tipo do arquivo: {profile_image.content_type}')
            return JsonResponse({
                'status': 'success',
                'filename': profile_image.name,
                'size': profile_image.size,
                'content_type': profile_image.content_type
            })

        return JsonResponse({'status': 'fail', 'error': 'Nenhum arquivo recebido.'}, status=400)

    return JsonResponse({'status': 'fail', 'error': 'Método não permitido.'}, status=405)
    