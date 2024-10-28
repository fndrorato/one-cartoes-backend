# custom_jwt.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adiciona campos extras ao token
        token['full_name'] = f'{user.first_name} {user.last_name}'
        token['roles'] = 'admin'  # Aqui você pode ajustar conforme seu sistema de roles

        return token
