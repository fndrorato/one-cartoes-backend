
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('users.urls')),    # As rotas de CRUD de usuários    
    path('api/v1/', include('clients.urls')),    # As rotas de CRUD de clientes e grupos de clientes    
    path('api/v1/', include('dashboards.urls')),    # As rotas de Dashboards
    path('api/v1/', include('payments.urls')),    # As rotas de Payments
]

# Adicione esta linha para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
