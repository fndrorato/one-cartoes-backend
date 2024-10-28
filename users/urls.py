# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GroupViewSet, 
    UserViewSet, 
    CustomTokenView,
    UserProfileUpdateView,
    ChangePasswordView,
    UserChangeClientUpdateView,
    ForgotPasswordView,
    ResetPasswordView,
    upload_profile_image
)

# Cria um roteador padrão para as rotas
router = DefaultRouter()
router.register(r'users', UserViewSet)  
router.register(r'users-groups', GroupViewSet)

# Define as URLs do app de usuários
urlpatterns = [
    path('auth/', CustomTokenView.as_view(), name='user-get-data'), 
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),    
    path('user/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('user/change-client/', UserChangeClientUpdateView.as_view(), name='user-client-update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    path('upload/', upload_profile_image, name='upload_profile_image'),
  

    # Inclui as rotas geradas automaticamente
    path('', include(router.urls)),
]




